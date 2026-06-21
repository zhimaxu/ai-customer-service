<template>
  <div class="dark-card" :class="{ hoverable }">
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>
    <div class="card-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  hoverable: { type: Boolean, default: true },
})
</script>

<style scoped>
.dark-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.dark-card.hoverable:hover {
  border-color: var(--border-medium);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

.card-header {
  padding: var(--space-4) var(--space-5) var(--space-3);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-body {
  padding: var(--space-5);
}
</style>
