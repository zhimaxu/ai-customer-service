<template>
  <div class="typing-indicator">
    <div class="avatar avatar-ai">AI</div>
    <div class="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</template>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
}

.avatar-ai {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--purple-accent), var(--purple-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.typing-dots span {
  width: 7px;
  height: 7px;
  background: var(--coral-primary);
  border-radius: 50%;
  display: inline-block;
  animation: typingWave 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }

@keyframes typingWave {
  0%, 80%, 100% {
    transform: scale(0.5);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
