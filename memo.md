# 备忘录

## Write 工具写入失败排查与解决方案

### 问题现象
Write/Bash 工具报错 "The required parameter `file_path` is missing" 或 "InputValidationError: Write was called with input that could not be parsed as JSON"，但短内容写入完全正常。

### 根因
当 tool call JSON payload 过长时（特别是 `content` 参数包含大量代码），可能在传输中被截断，导致 `file_path` 和 `content` 关键字段丢失。

### 分段写入策略（永久规则）

| 文件大小 | 策略 | 说明 |
|---------|------|------|
| < 50 行 | Write 直接写入 | 安全范围 |
| 50-100 行 | Write 直接写入 | 通常没问题 |
| 100-200 行 | **Edit 增量修改** | 先 Read 再局部替换，不要整体重写 |
| > 200 行 | **Bash heredoc** | `cat > path << 'EOF'` 写入 |

### 路径规则
- **必须用正斜杠**：`c:/Code/...` 而非 `c:\Code\...`
- **heredoc 分隔符用引号包裹**：`<< 'PYEOF'` 防止 shell 变量展开

### 示例
```bash
# 大文件 (>200行)
cat > c:/path/to/big_file.py << 'PYEOF'
...
PYEOF

# 中等文件 (50-200行) — 用 Edit 逐段替换
# 1. Read 文件
# 2. Edit 替换小块内容（每次 < 50 行）
```
