<template>
  <div class="agent-sidebar">
    <div class="sidebar-header">
      <h3>客服工作台</h3>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
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
      style="margin-bottom: 8px"
    />

    <div class="session-list">
      <div
        v-for="s in filteredSessions"
        :key="s.id"
        class="session-item"
        :class="{ active: currentSessionId === s.id }"
        @click="selectSession(s)"
      >
        <div class="session-info">
          <div class="session-header">
            <span class="session-user">{{ s.user_id }}</span>
            <el-tag :type="getStatusType(s.status)" size="small">{{ s.status }}</el-tag>
          </div>
          <div class="session-meta">
            <el-tag :type="s.current_agent_type === 'ai' ? 'info' : 'warning'" size="small">
              {{ s.current_agent_type === 'ai' ? 'AI' : '人工' }}
            </el-tag>
            <span>{{ s.message_count || 0 }} 条</span>
          </div>
        </div>
      </div>
      <div v-if="filteredSessions.length === 0" class="empty">暂无会话</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useAgentStore } from '../stores/agent'

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

function getStatusType(status) {
  const map = { active: 'success', human: 'warning', closed: 'info' }
  return map[status] || 'info'
}

function selectSession(session) {
  emit('select', session)
}
</script>

<style scoped>
.agent-sidebar {
  width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e0e0e0;
  background: #fafafa;
}
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}
.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}
.session-list {
  flex: 1;
  overflow-y: auto;
}
.session-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}
.session-item:hover {
  background: #f0f0f0;
}
.session-item.active {
  background: #e3f2fd;
  border-left: 3px solid #1976d2;
}
.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.session-user {
  font-weight: 500;
  font-size: 14px;
}
.session-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 8px;
  align-items: center;
}
.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
</style>
