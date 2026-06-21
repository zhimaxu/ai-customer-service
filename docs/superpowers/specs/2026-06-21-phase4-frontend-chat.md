# Phase 4: 前端聊天界面 — 设计文档

> 日期: 2026-06-21
> 状态: 已审批

---

## 目标

实现用户侧聊天界面：左右分栏布局、SSE 流式打字效果、会话管理、文件上传、OAuth2 认证。

**验收标准**：
- 登录页 → JWT token 管理
- 左右分栏：左侧会话列表 + 右侧聊天窗口
- SSE 流式逐字渲染 AI 回复（打字机效果）
- 文件拖拽上传（图片/PDF/Word）
- 打字速度可自定义（10ms–200ms）

---

## 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── public/
├── src/
│   ├── main.js                 # 入口：Pinia + Router + ElementPlus
│   ├── App.vue                 # 根组件：路由出口
│   ├── api/
│   │   ├── request.js          # Axios 实例（拦截器 + Token）
│   │   ├── chat.js             # 聊天 API（send, stream, sessions）
│   │   ├── knowledge.js        # 知识库 API
│   │   └── auth.js             # 认证 API（login, logout）
│   ├── stores/
│   │   ├── session.js          # Pinia：会话列表 + 当前会话
│   │   └── auth.js             # Pinia：登录状态 + Token
│   ├── views/
│   │   ├── Login.vue           # 登录页
│   │   └── ChatView.vue        # 聊天主页（左右分栏）
│   ├── components/
│   │   ├── SessionList.vue     # 会话列表 + 搜索 + 新建
│   │   ├── ChatWindow.vue      # 聊天区域容器
│   │   ├── MessageBubble.vue   # 单条消息气泡
│   │   ├── TypingIndicator.vue # 正在输入动画
│   │   ├── FileUpload.vue      # 文件上传组件
│   │   └── SettingsPanel.vue   # 设置面板（打字速度等）
│   └── router/
│       └── index.js            # 路由定义 + 导航守卫
```

---

## 核心组件设计

### 1. SSE 流式解析器 (`api/chat.js`)

**不使用 EventSource**（只支持 GET），改用 `fetch` + `ReadableStream`：

```javascript
// 解析 SSE 流
async function* parseSSE(response) {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value, { stream: true })
    buffer += chunk

    // 按双换行符分割事件
    const events = buffer.split('\n\n')
    buffer = events.pop() // 保留不完整的事件

    for (const event of events) {
      const lines = event.split('\n')
      let eventType = 'data'
      let data = ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7)
        } else if (line.startsWith('data: ')) {
          data = line.slice(6)
        }
      }

      if (eventType === 'chunk' || eventType === 'data') {
        yield { type: eventType, data: JSON.parse(data) }
      } else {
        yield { type: eventType, data: JSON.parse(data) }
      }
    }
  }
}
```

### 2. 聊天窗口 (`components/ChatWindow.vue`)

**职责**：
- 渲染消息列表（用户消息 + AI 回复）
- 处理 SSE 流式解析，逐字追加到 AI 回复
- 显示 TypingIndicator 动画
- 集成 FileUpload 组件
- 发送消息调用 `POST /api/chat/stream`

**打字机效果实现**：
- 收到 `chunk` 事件时，将 content 追加到当前 AI 消息
- 使用 `ref` 绑定消息内容，Vue 自动响应式更新
- 滚动条自动跟随到底部

### 3. 会话列表 (`components/SessionList.vue`)

**职责**：
- 调用 `GET /api/chat/sessions` 获取列表
- 搜索/过滤（按 user_id, channel, status）
- 新建会话（点击 + 按钮，自动创建）
- 关闭会话（DELETE 端点）
- 选中高亮

### 4. 文件上传 (`components/FileUpload.vue`)

**职责**：
- 拖拽上传区域
- 点击选择文件
- 支持格式：图片(PNG/JPG)、PDF、Word、Excel
- 上传到 `POST /api/knowledge/upload`
- 上传成功后自动将转换后的内容作为消息发送

### 5. 认证 (`views/Login.vue` + `stores/auth.js`)

**流程**：
1. 访问 `/chat` → 导航守卫检查 token → 无则跳转 `/login`
2. 登录页提交用户名密码
3. 后端返回 JWT → 存 localStorage + Pinia store
4. 每次 API 请求通过 Axios 拦截器自动附加 `Authorization: Bearer <token>`

---

## 数据流

```
用户输入消息
  │
  ▼
ChatWindow.vue → api/chat.js → POST /api/chat/stream
  │                                                    │
  │                                                    ▼
  │                                             Fetch + ReadableStream
  │                                                    │
  │                                                    ▼
  │                                             parseSSE() 解析事件
  │                                                    │
  │                         ┌──────────────────────────┼──────────┐
  │                         ▼                          ▼          ▼
  │                    event:chunk              event:done    event:error
  │                         │                          │           │
  │                         ▼                          ▼           ▼
  │                  追加到消息文本              停止loading    显示错误
  │                         │
  │                         ▼
  │                  自动滚动到底部
  │
  ▼
TypingIndicator 显示/隐藏
```

---

## 依赖

```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.5.0",
    "pinia": "^2.3.0",
    "element-plus": "^2.9.0",
    "@element-plus/icons-vue": "^2.3.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "vite": "^6.0.0"
  }
}
```

---

## 不包含的内容（Out of Scope）

- WebSocket 实时推送（Phase 5）
- 满意度评价弹窗（Phase 6）
- 客服工作台界面（Phase 5）
- 数据分析看板（Phase 6）
- 多语言切换（预留接口，Phase 3+）
