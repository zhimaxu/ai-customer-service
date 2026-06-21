<template>
  <div class="message-bubble" :class="[senderClass]">
    <span class="avatar">{{ avatarEmoji }}</span>
    <div class="bubble-content">
      <div class="bubble-text" v-html="formattedContent"></div>
      <div class="bubble-time">{{ time }}</div>
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

const avatarEmoji = computed(() => {
  if (props.sender === 'user') return '🧑'
  if (props.sender === 'agent') return '🧑‍♂️'
  return '🤖'
})

const senderClass = computed(() => `msg-${props.sender}`)

const formattedContent = computed(() => {
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
})
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  align-items: flex-start;
}
.msg-user { flex-direction: row; }
.msg-agent { flex-direction: row; }
.msg-assistant { flex-direction: row-reverse; }
.avatar { flex-shrink: 0; font-size: 24px; }
.bubble-content { max-width: 70%; }
.bubble-text {
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
}
.msg-user .bubble-text {
  background: #f5f5f5;
  color: #333;
  border-top-left-radius: 4px;
}
.msg-agent .bubble-text {
  background: #e8f5e9;
  color: #2e7d32;
  border-top-left-radius: 4px;
}
.msg-assistant .bubble-text {
  background: #1976d2;
  color: white;
  border-top-right-radius: 4px;
}
.bubble-time {
  font-size: 11px;
  color: #bbb;
  margin-top: 4px;
}
</style>
