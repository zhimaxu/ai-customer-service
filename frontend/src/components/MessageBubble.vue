<template>
  <div class="message-bubble" :class="[senderClass, { streaming }]">
    <span class="avatar">{{ sender === 'user' ? '🧑' : '🤖' }}</span>
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
  streaming: { type: Boolean, default: false },
})

const senderClass = computed(() => `msg-${props.sender}`)

const formattedContent = computed(() => {
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
})
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  align-items: flex-start;
}
.msg-user { flex-direction: row-reverse; }
.avatar { flex-shrink: 0; font-size: 24px; }
.bubble-content { max-width: 70%; }
.bubble-text {
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
}
.msg-user .bubble-text {
  background: #1976d2;
  color: white;
  border-top-right-radius: 4px;
}
.msg-assistant .bubble-text {
  background: #f5f5f5;
  color: #333;
  border-top-left-radius: 4px;
}
.bubble-time {
  font-size: 11px;
  color: #bbb;
  margin-top: 4px;
  text-align: right;
}
.msg-user .bubble-time { text-align: left; }
.streaming .bubble-text::after {
  content: '▋';
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
