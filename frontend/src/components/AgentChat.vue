<template>
  <div class="agent-chat">
    <div class="chat-header" v-if="sessionId">
      <div class="header-info">
        <span class="header-title">会话: {{ sessionId.slice(0, 8) }}...</span>
        <StatusDot status="active" />
      </div>
      <div class="header-actions">
        <el-button size="small" :icon="Camera" @click="handleTakeover" :disabled="isTakenOver" class="coral-sm-btn">
          转人工
        </el-button>
        <el-button size="small" type="danger" @click="handleClose" plain>关闭</el-button>
      </div>
    </div>
    <div class="chat-header" v-else>
      <span class="placeholder">请选择一个会话</span>
    </div>

    <div class="messages-area" ref="messagesRef">
      <div v-if="messages.length === 0 && sessionId" class="empty-messages">
        <el-icon :size="32"><ChatLineRound /></el-icon>
        <p>暂无消息</p>
      </div>
      <AgentMessageBubble
        v-for="(msg, idx) in messages"
        :key="idx"
        :sender="msg.sender"
        :content="msg.content"
        :time="msg.time"
      />
    </div>

    <!-- Quick reply bar -->
    <div class="quick-reply-bar" v-if="sessionId">
      <span class="quick-label">快捷回复:</span>
      <el-button
        v-for="(reply, idx) in quickReplies"
        :key="idx"
        size="small"
        @click="handleQuickReply(reply)"
        class="quick-pill"
      >
        {{ reply.substring(0, 12) }}{{ reply.length > 12 ? '...' : '' }}
      </el-button>
    </div>

    <div class="input-area glass" v-if="sessionId">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        placeholder="输入回复... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="sendMessage"
        class="dark-input"
      />
      <el-button type="primary" @click="sendMessage" :disabled="!inputText.trim()" class="coral-send-btn">
        <el-icon><Promotion /></el-icon>
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Promotion, Camera, ChatLineRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAgentStore } from '../stores/agent'
import AgentMessageBubble from './AgentMessageBubble.vue'
import StatusDot from './StatusDot.vue'

const props = defineProps({
  sessionId: String,
})

const agentStore = useAgentStore()
const inputText = ref('')
const messagesRef = ref(null)
const messages = ref([])
const isTakenOver = ref(false)

const quickReplies = computed(() => agentStore.quickReplies)

watch(() => props.sessionId, async (newId) => {
  if (newId) {
    isTakenOver.value = false
    try {
      const data = await agentStore.fetchSessionMessages(newId)
      messages.value = (data || []).map((m) => ({
        sender: m.sender || 'assistant',
        content: m.content || m.message || '',
        time: m.created_at ? new Date(m.created_at).toLocaleTimeString() : '',
      }))
      scrollToBottom()
    } catch (e) {
      console.error('Failed to fetch messages:', e)
    }
    agentStore.connectToSession(newId)
  }
})

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || !props.sessionId) return

  messages.value.push({
    sender: 'agent',
    content: text,
    time: new Date().toLocaleTimeString(),
  })
  inputText.value = ''
  scrollToBottom()

  try {
    await agentStore.replyToSession(props.sessionId, text)
  } catch (error) {
    ElMessage.error('发送失败: ' + error)
  }
}

async function handleQuickReply(content) {
  if (!props.sessionId) return
  messages.value.push({
    sender: 'agent',
    content,
    time: new Date().toLocaleTimeString(),
  })
  scrollToBottom()

  try {
    await agentStore.quickReplyToSession(props.sessionId, content)
  } catch (error) {
    ElMessage.error('发送失败: ' + error)
  }
}

async function handleTakeover() {
  if (!props.sessionId) return
  try {
    await agentStore.takeoverSession(props.sessionId)
    isTakenOver.value = true
    ElMessage.success('已接管会话')
  } catch (error) {
    ElMessage.error('接管失败: ' + error)
  }
}

function handleClose() {
  if (!props.sessionId) return
  agentStore.closeSession(props.sessionId).then(() => {
    ElMessage.success('会话已关闭')
  })
}
</script>

<style scoped>
.agent-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-deep);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-surface);
}

.header-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.header-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.coral-sm-btn {
  background: var(--coral-primary) !important;
  border: none !important;
  color: white !important;
  border-radius: var(--radius-sm) !important;
  font-size: 12px !important;
  padding: 0 var(--space-3) !important;
}

.placeholder {
  color: var(--text-muted);
  font-size: 14px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
}

.empty-messages {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-16) 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.empty-messages p {
  margin: 0;
  font-size: 14px;
}

.quick-reply-bar {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  flex-wrap: wrap;
  background: var(--bg-surface);
  align-items: center;
}

.quick-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-right: var(--space-2);
  white-space: nowrap;
}

.quick-pill {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-subtle) !important;
  color: var(--text-secondary) !important;
  border-radius: var(--radius-full) !important;
  font-size: 12px !important;
  padding: 2px var(--space-3) !important;
  transition: all var(--transition-fast);
}

.quick-pill:hover {
  background: rgba(255, 107, 53, 0.1) !important;
  border-color: var(--coral-primary) !important;
  color: var(--coral-primary) !important;
}

.input-area {
  padding: var(--space-3) var(--space-4);
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
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
