<template>
  <div class="chat-window">
    <div class="messages-area" ref="messagesRef">
      <div v-if="messages.length === 0" class="welcome">
        <h2>欢迎使用 AI 智能客服</h2>
        <p>选择或创建一个会话开始对话</p>
      </div>
      <MessageBubble
        v-for="(msg, idx) in messages"
        :key="msg.id || idx"
        :sender="msg.sender"
        :content="msg.content"
        :time="msg.time"
      />
      <TypingIndicator v-if="isStreaming" />
    </div>

    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="sendMessage"
      />
      <el-button type="primary" @click="sendMessage" :disabled="!inputText.trim()" :icon="Promotion">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
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
            content: 'Error: ' + parsed.detail,
            time: new Date().toLocaleTimeString(),
          })
        }
      }
    }
  } catch (error) {
    sessionStore.addMessage({
      sender: 'assistant',
      content: 'Failed to send: ' + error.message,
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
  padding: 20px;
}
.welcome {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}
.welcome h2 { color: #333; margin-bottom: 8px; }
.input-area {
  border-top: 1px solid #e0e0e0;
  padding: 12px;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: #fff;
}
.input-area .el-textarea { flex: 1; }
</style>
