<template>
  <span class="status-dot" :class="statusClass" :title="statusLabel"></span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'active' },
})

const statusClass = computed(() => {
  const map = { active: 'online', human: 'busy', closed: 'offline' }
  return map[props.status] || 'offline'
})

const statusLabel = computed(() => {
  const map = { online: '活跃', busy: '人工服务', offline: '已关闭' }
  return map[statusClass.value] || '未知'
})
</script>

<style scoped>
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.online {
  background: var(--success);
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
  animation: pulse 2s infinite;
}

.status-dot.busy {
  background: var(--warning);
  box-shadow: 0 0 6px rgba(251, 191, 36, 0.5);
}

.status-dot.offline {
  background: var(--text-muted);
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.85); }
}
</style>
