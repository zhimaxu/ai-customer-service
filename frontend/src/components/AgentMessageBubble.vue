<template>
  <div class="message-bubble" :class="[senderClass]">
    <div class="avatar" :class="avatarClass">{{ avatarLetter }}</div>
    <div class="bubble-wrapper">
      <div class="bubble-content">
        <div class="bubble-text" v-html="formattedContent"></div>
        <div class="bubble-time">{{ time }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  sender: { type: String, default: 'user' },
  content: { type: String, default: '' },
  time: { type: String, default: '' },
})

const avatarLetter = computed(() => {
  if (props.sender === 'user') return 'U'
  if (props.sender === 'agent') return 'A'
  return 'AI'
})

const avatarClass = computed(() => {
  if (props.sender === 'user') return 'avatar-user'
  if (props.sender === 'agent') return 'avatar-agent'
  return 'avatar-assistant'
})

const senderClass = computed(() => {
  const map = { user: 'msg-left', agent: 'msg-left', assistant: 'msg-right' }
  return map[props.sender] || 'msg-left'
})

const formattedContent = computed(() => {
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
})
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  align-items: flex-start;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-left { flex-direction: row; }
.msg-right { flex-direction: row-reverse; }

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.avatar-user {
  background: linear-gradient(135deg, var(--text-muted), var(--text-secondary));
}

.avatar-agent {
  background: linear-gradient(135deg, var(--success), #6EE7B7);
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.3);
}

.avatar-assistant {
  background: linear-gradient(135deg, var(--purple-accent), var(--purple-light));
  box-shadow: var(--shadow-glow-purple);
}

.bubble-wrapper {
  max-width: 70%;
}

.msg-right .bubble-wrapper {
  align-self: flex-end;
}

.bubble-text {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.msg-left .bubble-text {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-top-left-radius: var(--radius-sm);
}

.msg-right .bubble-text {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  color: var(--text-inverse);
  border-top-right-radius: var(--radius-sm);
}

.bubble-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  font-family: SF Mono, Consolas, monospace;
}

.msg-left .bubble-time { text-align: left; }
.msg-right .bubble-time { text-align: right; }
</style>
