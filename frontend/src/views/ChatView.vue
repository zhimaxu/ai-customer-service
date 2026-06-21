<template>
  <div class="chat-view">
    <div class="top-bar">
      <span class="logo">AI 智能客服</span>
      <div class="top-actions">
        <el-button :icon="Setting" @click="settingsRef.open = true" />
        <el-button :icon="SwitchButton" @click="handleLogout">退出</el-button>
      </div>
    </div>

    <div class="main-area">
      <SessionList
        :current-session="sessionStore.currentSession"
        @select="handleSelectSession"
        @new="handleNewSession"
      />
      <ChatWindow />
    </div>
  </div>

  <SettingsPanel ref="settingsRef" />
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Setting, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useSessionStore } from '../stores/session'
import SessionList from '../components/SessionList.vue'
import ChatWindow from '../components/ChatWindow.vue'
import SettingsPanel from '../components/SettingsPanel.vue'

const router = useRouter()
const authStore = useAuthStore()
const sessionStore = useSessionStore()
const settingsRef = ref(null)

async function handleNewSession() {
  await sessionStore.createSession()
  ElMessage.success('新会话已创建')
}

async function handleSelectSession(session) {
  await sessionStore.fetchSessionDetail(session.id)
}

function handleLogout() {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.chat-view {
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
  background: #1976d2;
  color: white;
}
.logo { font-size: 18px; font-weight: bold; }
.top-actions .el-button { color: white; }
.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
