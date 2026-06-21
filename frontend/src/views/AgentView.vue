<template>
  <div class="agent-view">
    <div class="main-area">
      <AgentSidebar :current-session-id="selectedSessionId" @select="handleSelectSession" />
      <AgentChat :session-id="selectedSessionId" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
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
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.agent-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
