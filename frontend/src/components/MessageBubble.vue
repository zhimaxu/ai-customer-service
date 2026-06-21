<template>
  <div class="message-bubble" :class="[senderClass, { streaming }]">
    <div class="avatar" :class="senderClass">
      {{ avatarLetter }}
    </div>
    <div class="bubble-wrapper">
      <div class="bubble-content">
        <div class="bubble-text" v-html="formattedContent"></div>
        <div class="bubble-footer">
          <span class="bubble-time">{{ time }}</span>
          <span v-if="streaming" class="streaming-dot"></span>
        </div>
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
  streaming: { type: Boolean, default: false },
})

const avatarLetter = computed(() => {
  if (props.sender === 'user') return 'U'
  return 'AI'
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
  gap: var(--space-3);
  padding: var(--space-2) 0;
  align-items: flex-start;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.msg-user {
  flex-direction: row-reverse;
}

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

.msg-user .avatar {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  box-shadow: var(--shadow-glow-coral);
}

.msg-assistant .avatar {
  background: linear-gradient(135deg, var(--purple-accent), var(--purple-light));
  box-shadow: var(--shadow-glow-purple);
}

.bubble-wrapper {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.msg-user .bubble-wrapper {
  align-items: flex-end;
}

.bubble-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bubble-text {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.msg-user .bubble-text {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  color: var(--text-inverse);
  border-top-right-radius: var(--radius-sm);
}

.msg-assistant .bubble-text {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-top-left-radius: var(--radius-sm);
}

.bubble-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-end;
}

.bubble-time {
  font-size: 11px;
  color: var(--text-muted);
  font-family: SF Mono, Consolas, monospace;
}

.streaming-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--coral-primary);
  border-radius: 50%;
  animation: pulseDot 1.2s infinite ease-in-out;
}

@keyframes pulseDot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
