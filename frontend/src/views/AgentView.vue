<template>
  <div class="agent-view">
    <div class="top-bar">
      <span class="logo">?? 客服工作台</span>
      <div class="top-actions">
        <el-badge :value="agentStore.unreadCount" :hidden="agentStore.unreadCount === 0">
          <el-button :icon="Bell" circle />
        </el-badge>
        <el-button :icon="SwitchButton" @click="handleLogout">退出</el-button>
      </div>
    </div>

    <div class="main-area">
      <AgentSidebar :current-session-id="selectedSessionId" @select="handleSelectSession" />
      <AgentChat :session-id="selectedSessionId" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useAgentStore } from '../stores/agent'
import AgentSidebar from '../components/AgentSidebar.vue'
import AgentChat from '../components/AgentChat.vue'

const router = useRouter()
const authStore = useAuthStore()
const agentStore = useAgentStore()
const selectedSessionId = ref('')

function handleSelectSession(session) {
  selectedSessionId.value = session.id
}

function handleLogout() {
  authStore.logout()
  agentStore.disconnect()
  ElMessage.success('??')
  router.push('/login')
}
</script>

<style scoped>
.agent-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  height: 48px;
  background: #2e7d32;
  color: white;
}
.logo {
  font-size: 18px;
  font-weight: bold;
}
.top-actions .el-button {
  color: white;
}
.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
