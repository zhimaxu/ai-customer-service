<template>
  <div class="skeleton-loader" :class="skeletonType">
    <div v-for="n in lines" :key="n" class="skeleton-line"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  lines: { type: Number, default: 3 },
  type: { type: String, default: 'text' },
})

const skeletonType = computed(() => `skeleton-${props.type}`)
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skeleton-line {
  height: 12px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-surface) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-line:last-child {
  width: 60%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
