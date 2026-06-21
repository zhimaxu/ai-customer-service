<template>
  <div class="agent-chat">
    <div class="chat-header" v-if="sessionId">
      <span>会话: {{ sessionId }}</span>
      <div class="header-actions">
        <el-button size="small" :icon="SwitchCamera" @click="handleTakeover" :disabled="isTakenOver">
          转人工
        </el-button>
        <el-button size="small" type="danger" @click="handleClose">关闭</el-button>
      </div>
    </div>
    <div class="chat-header" v-else>
      <span class="placeholder">请选择一个会话</span>
    </div>

    <div class="messages-area" ref="messagesRef">
      <div v-if="messages.length === 0 && sessionId" class="empty-messages">
        暂无消息
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
      <el-button
        v-for="(reply, idx) in quickReplies"
        :key="idx"
        size="small"
        @click="handleQuickReply(reply)"
      >
        {{ reply.substring(0, 8) }}...
      </el-button>
    </div>

    <div class="input-area" v-if="sessionId">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        placeholder="输入回复... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="sendMessage"
      />
      <el-button type="primary" @click="sendMessage" :disabled="!inputText.trim()" :icon="Promotion">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Promotion, SwitchCamera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAgentStore } from '../stores/agent'
import AgentMessageBubble from './AgentMessageBubble.vue'

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
  background: #fff;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.placeholder {
  color: #999;
}
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.empty-messages {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
.quick-reply-bar {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
  background: #fafafa;
}
.input-area {
  padding: 12px;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  border-top: 1px solid #e0e0e0;
}
.input-area .el-textarea {
  flex: 1;
}
</style>
