<template>
  <div class="agent-sidebar">
    <div class="sidebar-header">
      <h3>客服工作台</h3>
      <el-badge :value="agentStore.unreadCount" :hidden="agentStore.unreadCount === 0" class="unread-badge">
        <el-icon :size="16"><Bell /></el-icon>
      </el-badge>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="dark-tabs">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="AI" name="ai" />
      <el-tab-pane label="人工" name="agent" />
      <el-tab-pane label="已关闭" name="closed" />
    </el-tabs>

    <el-input
      v-model="searchQuery"
      placeholder="搜索用户..."
      :prefix-icon="Search"
      clearable
      size="small"
      class="dark-input"
      style="margin-bottom: var(--space-3)"
    />

    <div class="session-list">
      <div
        v-for="(s, idx) in filteredSessions"
        :key="s.id"
        class="session-item"
        :class="{ active: currentSessionId === s.id }"
        @click="selectSession(s)"
      >
        <div class="session-info">
          <div class="session-header">
            <span class="session-user">{{ s.user_id }}</span>
            <StatusDot :status="s.status" />
          </div>
          <div class="session-tags">
            <el-tag
              :type="s.current_agent_type === 'ai' ? 'danger' : 'warning'"
              size="small"
              class="agent-tag"
              effect="plain"
            >
              {{ s.current_agent_type === 'ai' ? 'AI' : '人工' }}
            </el-tag>
            <span class="msg-count">{{ s.message_count || 0 }} 条</span>
          </div>
        </div>
      </div>
      <div v-if="filteredSessions.length === 0" class="empty">暂无会话</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Bell } from '@element-plus/icons-vue'
import { useAgentStore } from '../stores/agent'
import StatusDot from './StatusDot.vue'

const props = defineProps({
  currentSessionId: String,
})

const emit = defineEmits(['select'])

const agentStore = useAgentStore()
const activeTab = ref('all')
const searchQuery = ref('')

onMounted(() => {
  agentStore.fetchSessions()
})

const filteredSessions = computed(() => {
  let list = agentStore.sessions
  if (activeTab.value === 'ai') {
    list = list.filter((s) => s.current_agent_type === 'ai')
  } else if (activeTab.value === 'agent') {
    list = list.filter((s) => s.current_agent_type === 'agent')
  } else if (activeTab.value === 'closed') {
    list = list.filter((s) => s.status === 'closed')
  }
  if (searchQuery.value) {
    list = list.filter((s) => s.user_id?.includes(searchQuery.value))
  }
  return list
})

function handleTabChange(tab) {
  if (tab === 'all') {
    agentStore.fetchSessions()
  } else if (tab === 'ai') {
    agentStore.fetchSessions({ agent_type: 'ai' })
  } else if (tab === 'agent') {
    agentStore.fetchSessions({ agent_type: 'agent' })
  } else if (tab === 'closed') {
    agentStore.fetchSessions({ status: 'closed' })
  }
}

function selectSession(session) {
  emit('select', session)
}
</script>

<style scoped>
.agent-sidebar {
  width: 320px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-surface);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.unread-badge {
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.unread-badge:hover {
  color: var(--coral-primary);
}

:deep(.dark-tabs .el-tabs__header) {
  border-bottom: 1px solid var(--border-subtle);
  margin: 0;
}

:deep(.dark-tabs .el-tabs__item) {
  color: var(--text-muted) !important;
  border-color: var(--border-subtle) !important;
}

:deep(.dark-tabs .el-tabs__item.is-active) {
  color: var(--coral-primary) !important;
}

:deep(.dark-tabs .el-tabs__active-bar) {
  background: var(--coral-primary) !important;
}

:deep(.dark-tabs .el-tabs__content) {
  display: none;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

.session-item {
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

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.session-user {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}

.session-tags {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.agent-tag {
  font-size: 11px !important;
  border-radius: var(--radius-sm) !important;
}

.msg-count {
  font-size: 12px;
  color: var(--text-muted);
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
