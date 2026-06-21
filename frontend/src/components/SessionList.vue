<template>
  <div class="session-list">
    <div class="list-header">
      <h3>会话列表</h3>
      <el-button type="primary" size="small" class="coral-sm-btn" :icon="Plus" @click="handleNew">
        新建
      </el-button>
    </div>
    <el-input
      v-model="searchQuery"
      placeholder="搜索会话..."
      :prefix-icon="Search"
      clearable
      size="small"
      class="dark-input"
      style="margin-bottom: var(--space-3)"
    />
    <div class="session-items">
      <div
        v-for="s in filteredSessions"
        :key="s.id"
        class="session-item"
        :class="{ active: currentSession?.id === s.id }"
        @click="selectSession(s)"
      >
        <div class="session-info">
          <div class="session-title-row">
            <span class="session-title">{{ s.user_id }}</span>
            <StatusDot :status="s.status" />
          </div>
          <div class="session-preview">
            共 {{ s.message_count || 0 }} 条消息
          </div>
        </div>
        <el-button
          size="small"
          :icon="Delete"
          circle
          text
          class="close-btn"
          @click.stop="handleClose(s.id)"
          v-if="currentSession?.id === s.id"
        />
      </div>
      <div v-if="filteredSessions.length === 0" class="empty">暂无会话</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus, Search, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useSessionStore } from '../stores/session'
import StatusDot from './StatusDot.vue'

const props = defineProps({
  currentSession: Object,
})

const emit = defineEmits(['select', 'new', 'close'])

const sessionStore = useSessionStore()
const searchQuery = ref('')

const filteredSessions = computed(() => {
  if (!searchQuery.value) return sessionStore.sessions
  return sessionStore.sessions.filter((s) =>
    s.user_id?.includes(searchQuery.value)
  )
})

function selectSession(s) {
  emit('select', s)
}

function handleNew() {
  emit('new')
}

function handleClose(id) {
  sessionStore.closeSession(id).then(() => {
    ElMessage.success('会话已关闭')
  })
}
</script>

<style scoped>
.session-list {
  width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-surface);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.coral-sm-btn {
  background: var(--coral-primary) !important;
  border: none !important;
  color: white !important;
  border-radius: var(--radius-sm) !important;
  font-size: 12px !important;
}

.session-items {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  border-bottom: 1px solid var(--border-subtle);
  transition: all var(--transition-fast);
  position: relative;
}

.session-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--coral-primary);
  transform: scaleY(0);
  transition: transform var(--transition-fast);
}

.session-item:hover {
  background: var(--bg-elevated);
}

.session-item.active {
  background: rgba(255, 107, 53, 0.06);
}

.session-item.active::before {
  transform: scaleY(1);
}

.session-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.session-title {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}

.session-preview {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.close-btn {
  color: var(--text-muted);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.session-item:hover .close-btn {
  opacity: 1;
}

.close-btn:hover {
  color: var(--danger) !important;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-10) 0;
  font-size: 13px;
}

:deep(.dark-input .el-input__wrapper) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  box-shadow: none !important;
  border-radius: var(--radius-sm) !important;
}

:deep(.dark-input .el-input__inner) {
  color: var(--text-primary) !important;
  font-size: 12px !important;
}

:deep(.dark-input .el-input__wrapper.is-focus) {
  border-color: var(--coral-primary) !important;
}
</style>
