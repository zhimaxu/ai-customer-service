# Phase 2: 聊天核心 — 设计文档

> 日期: 2026-06-20
> 状态: 已审批

---

## 目标

在 Phase 1 后端骨架基础上，实现完整的聊天核心能力：多轮对话、SSE 流式回复、RAG 知识检索、会话管理。

**验收标准**：
- `POST /api/chat/stream` 返回 SSE 流式回复，AI 首字响应 < 3s
- 多轮对话上下文通过滑动窗口 + 动态摘要管理
- RAG 检索从 Qdrant 知识库返回相关文档片段
- 会话 CRUD 接口可用

---

## 架构变更

### 新增 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/stream` | SSE 流式回复（结构化事件） |
| POST | `/api/chat` | 一次性完整回复（现有，需增强） |
| GET | `/api/chat/sessions` | 获取用户会话列表 |
| GET | `/api/chat/sessions/{id}` | 获取会话详情及消息历史 |
| DELETE | `/api/chat/sessions/{id}` | 关闭/删除会话 |
| GET | `/api/ws/chat/{id}` | WebSocket 端点（暂不实现，Phase 5） |

### 核心组件

```
backend/app/
├── api/
│   ├── chat.py          ← 重构：拆分 stream / sessions
│   └── __init__.py      ← 更新路由挂载
├── services/
│   ├── chat_service.py  ← 重构：滑动窗口 + 摘要 + RAG
│   ├── rag_service.py   ← 新增：RAG 检索编排
│   └── summarize_service.py ← 新增：对话摘要
├── schemas/
│   └── chat.py          ← 扩展：SessionResponse, SSE event schemas
├── models/
│   └── session.py       ← 无需改动（已有 Session/Message/Satisfaction）
└── core/
    └── qdrant_client.py ← 无需改动（已有基础设施）
```

### 数据流

```
用户消息
  │
  ▼
[1] 查找/创建 Session
  │
  ▼
[2] 检索历史消息（滑动窗口）
  │
  ▼
[3] RAG 检索知识库（Top-K 相关片段）
  │
  ▼
[4] 动态摘要（窗口超限 → summarization）
  │
  ▼
[5] 构建 Prompt: system + 知识库 + 摘要 + 对话窗口
  │
  ▼
[6] 调用 Agnes AI
  │   ├─ 非流式 → 完整回复
  │   └─ 流式 → SSE 事件推送
  │
  ▼
[7] 保存用户消息 + AI 回复
  │
  ▼
返回结果
```

---

## 关键技术设计

### 1. 滑动窗口 + 动态摘要

**策略**：
- 维护最近 N=10 轮对话（20 条消息）作为滑动窗口
- 超出部分提取最早的对话，调用 Agnes AI 生成摘要
- 摘要与滑动窗口一起传入 prompt

**摘要逻辑**：
```python
# 如果历史消息 > 20 条：
# 1. 保留最近 20 条（滑动窗口）
# 2. 将更早的消息分组（每组 10 条），逐组摘要
# 3. 最终 prompt = system + 知识库摘要 + 对话摘要链 + 滑动窗口
```

**摘要 Prompt**：
```
请总结以下客服对话的核心内容，保留关键问题和答案要点，
忽略寒暄用语。输出 3-5 句话的摘要。
<对话历史>
```

### 2. RAG 检索

**流程**：
1. 对用户最新消息调用 Agnes AI embedding
2. 在 Qdrant `knowledge_vectors` 集合中做向量检索（cosine distance）
3. 取 Top-K=3 个文档片段
4. 将检索结果拼入 system prompt 作为知识库上下文

**检索参数**：
- `limit=3`（最多 3 个相关片段）
- `score_threshold=0.5`（相似度低于 0.5 的不返回）
- payload filter: `tenant_id` 隔离

**Prompt 注入格式**：
```
以下是相关知识库内容，供参考回答用户问题：
<knowledge_context>
片段1: ...
片段2: ...
片段3: ...
</knowledge_context>
如果知识库中没有相关内容，请告知用户并建议转人工。
```

### 3. SSE 流式事件

**事件类型**：

```json
// 内容块
{"type": "chunk", "content": "您好，"}

// 完成
{"type": "done", "session_id": "xxx", "token_count": 128}

// 错误
{"type": "error", "detail": "服务暂时不可用"}

// 心跳（可选，防止超时）
{"type": "ping"}
```

**实现方式**：
- 使用 FastAPI 的 `StreamingResponse` + `text/event-stream`
- Agnes AI 的 `chat_stream` 返回 SSE 原始流
- 在服务端解析 Agnes 的 chunk 事件，转换为结构化 JSON 事件后转发

**超时设置**：
- 单个 SSE 连接超时 60s
- Agnes AI 请求超时 30s
- 首字延迟（TTFT）监控

### 4. 会话管理

**新增字段**（Message 表已有，Session 表增强）：
- `last_message_at`: 最后一条消息时间
- `message_count`: 消息总数（可选，可实时 COUNT）
- `query_count`: 知识库查询次数（用于统计）

**会话列表接口**：
```json
GET /api/chat/sessions?user_id=xxx&channel=web&page=1&page_size=20
// 返回: { "sessions": [...], "total": 100, "page": 1 }
```

**会话详情接口**：
```json
GET /api/chat/sessions/{id}
// 返回: { "session": {...}, "messages": [...] }
```

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| Agnes AI 超时 | 返回 504，SSE 发 `{"type": "error", "detail": "AI 响应超时"}` |
| Qdrant 不可用 | 降级为无 RAG 模式，日志告警 |
| 数据库写入失败 | 回滚事务，返回 500 |
| 空知识库检索 | 正常流程，不注入知识库上下文 |
| 摘要生成失败 | 跳过摘要，只传滑动窗口 |

---

## 依赖关系

- **Phase 1**：数据模型、Qdrant 集合、Agnes AI 封装
- **Phase 3**：知识库管理（RAG 的数据来源，Phase 2 假设已有数据）
- **Phase 4**：前端聊天界面（消费 SSE 流式接口）
- **Phase 5**：WebSocket 实时推送（复用此阶段的会话管理逻辑）

---

## 不包含的内容（Out of Scope）

- WebSocket 实时通信（Phase 5）
- 图片/视频消息处理（Phase 3+）
- 满意度评价（已有模型，Phase 6 实现 API）
- 客服接管（Phase 5）
- 前端界面（Phase 4）
