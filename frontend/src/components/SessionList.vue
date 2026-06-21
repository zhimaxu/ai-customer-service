<template>
  <div class="session-list">
    <div class="list-header">
      <h3>会话列表</h3>
      <el-button type="primary" size="small" :icon="Plus" @click="handleNew">新会话</el-button>
    </div>
    <el-input
      v-model="searchQuery"
      placeholder="搜索会话..."
      :prefix-icon="Search"
      clearable
      size="small"
      style="margin-bottom: 12px"
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
          <div class="session-title">{{ s.user_id }}</div>
          <div class="session-meta">
            {{ s.status }} · {{ s.message_count || 0 }} 条消息
          </div>
        </div>
        <el-button
          size="small"
          :icon="Delete"
          circle
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
  border-right: 1px solid #e0e0e0;
  background: #fafafa;
}
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}
.list-header h3 {
  margin: 0;
  font-size: 16px;
}
.session-items {
  flex: 1;
  overflow-y: auto;
}
.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
.session-title {
  font-weight: 500;
  font-size: 14px;
}
.session-meta {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
</style>
