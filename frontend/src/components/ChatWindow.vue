<template>
  <div class="chat-window dot-grid-bg">
    <div class="messages-area" ref="messagesRef">
      <div v-if="messages.length === 0" class="welcome">
        <div class="welcome-icon">
          <el-icon :size="48"><ChatDotRound /></el-icon>
        </div>
        <h2>欢迎使用 AI 智能客服</h2>
        <p>选择或创建一个会话开始对话</p>
      </div>
      <MessageBubble
        v-for="(msg, idx) in messages"
        :key="msg.id || idx"
        :sender="msg.sender"
        :content="msg.content"
        :time="msg.time"
        :streaming="idx === messages.length - 1 && isStreaming"
      />
      <TypingIndicator v-if="isStreaming && messages.length === 0" />
    </div>

    <div class="input-area glass">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="sendMessage"
        class="dark-input"
      />
      <el-button
        type="primary"
        @click="sendMessage"
        :disabled="!inputText.trim()"
        class="coral-send-btn"
      >
        <el-icon><Promotion /></el-icon>
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { Promotion, ChatDotRound } from '@element-plus/icons-vue'
import { useSessionStore } from '../stores/session'
import MessageBubble from './MessageBubble.vue'
import TypingIndicator from './TypingIndicator.vue'

const sessionStore = useSessionStore()
const inputText = ref('')
const messagesRef = ref(null)
const isStreaming = ref(false)

const messages = computed(() => sessionStore.messages)

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(() => sessionStore.messages.length, scrollToBottom)

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return

  const userMsg = {
    sender: 'user',
    content: text,
    time: new Date().toLocaleTimeString(),
  }
  sessionStore.addMessage(userMsg)
  inputText.value = ''
  scrollToBottom()

  isStreaming.value = true
  scrollToBottom()

  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        user_id: sessionStore.currentSession?.user_id || 'current-user',
        session_id: sessionStore.currentSession?.id,
        tenant_id: 'default',
      }),
    })

    if (!resp.ok) throw new Error('HTTP ' + resp.status)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let assistantContent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const events = buffer.split('\n\n')
      buffer = events.pop()

      for (const event of events) {
        const lines = event.split('\n')
        let eventType = 'data'
        let dataStr = ''

        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7)
          else if (line.startsWith('data: ')) dataStr = line.slice(6)
        }

        if (eventType === 'chunk' && dataStr) {
          const parsed = JSON.parse(dataStr)
          assistantContent += parsed.content || ''
          const lastMsg = sessionStore.messages[sessionStore.messages.length - 1]
          if (lastMsg && lastMsg.sender === 'assistant') {
            lastMsg.content = assistantContent
          } else {
            sessionStore.addMessage({
              sender: 'assistant',
              content: assistantContent,
              time: new Date().toLocaleTimeString(),
            })
          }
          scrollToBottom()
        } else if (eventType === 'done' && dataStr) {
          const parsed = JSON.parse(dataStr)
          if (sessionStore.currentSession?.id !== parsed.session_id) {
            sessionStore.currentSession = { id: parsed.session_id }
          }
        } else if (eventType === 'error' && dataStr) {
          const parsed = JSON.parse(dataStr)
          sessionStore.addMessage({
            sender: 'assistant',
            content: '出错了: ' + parsed.detail,
            time: new Date().toLocaleTimeString(),
          })
        }
      }
    }
  } catch (error) {
    sessionStore.addMessage({
      sender: 'assistant',
      content: '发送失败: ' + error.message,
      time: new Date().toLocaleTimeString(),
    })
  } finally {
    isStreaming.value = false
  }
}
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.welcome {
  text-align: center;
  padding: var(--space-16) var(--space-6);
  color: var(--text-muted);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto var(--space-4);
  background: linear-gradient(135deg, var(--coral-primary), var(--purple-accent));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-glow-coral);
}

.welcome h2 {
  font-size: 22px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 var(--space-2) 0;
}

.welcome p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.input-area {
  padding: var(--space-3) var(--space-4);
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
  border-top: 1px solid var(--border-subtle);
}

.input-area .el-textarea {
  flex: 1;
}

:deep(.dark-input .el-textarea__inner) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
}

:deep(.dark-input .el-textarea__inner:focus) {
  border-color: var(--coral-primary) !important;
  box-shadow: 0 0 0 1px var(--coral-primary) !important;
}

.coral-send-btn {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light)) !important;
  border: none !important;
  color: white !important;
  border-radius: var(--radius-md) !important;
  padding: 0 var(--space-4) !important;
  font-weight: 600 !important;
  box-shadow: var(--shadow-glow-coral);
  transition: all var(--transition-base);
  white-space: nowrap;
}

.coral-send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 24px rgba(255, 107, 53, 0.4) !important;
}

.coral-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
