<template>
  <el-drawer v-model="open" title="设置" :direction="direction" size="380px" class="dark-drawer">
    <div class="drawer-content">
      <el-form label-position="top">
        <el-form-item label="打字速度 (ms/字)">
          <el-slider v-model="speed" :min="10" :max="200" :step="5" show-input class="dark-slider" />
          <span style="font-size: 12px; color: var(--text-muted)">默认 30ms，越小越快</span>
        </el-form-item>

        <el-form-item label="主题">
          <el-radio-group v-model="theme" class="dark-radio-group">
            <el-radio-button value="light">浅色</el-radio-button>
            <el-radio-button value="dark">深色</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref } from 'vue'
const open = ref(false)
const direction = ref('rtl')
const speed = ref(parseInt(localStorage.getItem('typewriter-speed') || '30'))
const theme = ref(localStorage.getItem('theme') || 'light')
defineExpose({ open })
</script>

<style scoped>
.drawer-content {
  padding: var(--space-4) 0;
}

:deep(.dark-drawer .el-drawer__header) {
  color: var(--text-primary) !important;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: var(--space-4);
  margin-bottom: var(--space-4);
}

:deep(.dark-drawer .el-drawer__body) {
  color: var(--text-primary);
}

:deep(.dark-slider .el-slider__runway) {
  background-color: var(--bg-elevated) !important;
}

:deep(.dark-slider .el-slider__bar) {
  background-color: var(--coral-primary) !important;
}

:deep(.dark-slider .el-slider__button) {
  border-color: var(--coral-primary) !important;
  background-color: var(--coral-primary) !important;
}

:deep(.dark-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: var(--coral-primary) !important;
  border-color: var(--coral-primary) !important;
  color: white !important;
}

:deep(.dark-radio-group .el-radio-button__inner) {
  background-color: var(--bg-elevated) !important;
  border-color: var(--border-subtle) !important;
  color: var(--text-secondary) !important;
}
</style>
