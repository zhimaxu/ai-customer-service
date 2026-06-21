<template>
  <div class="sidebar-nav" :class="{ expanded }">
    <div class="sidebar-toggle" @click="toggle">
      <el-icon :size="20"><component :is="expandIcon" /></el-icon>
    </div>

    <nav class="sidebar-menu">
      <router-link to="/" class="nav-item" active-class="active">
        <el-icon :size="20"><ChatDotRound /></el-icon>
        <span class="nav-label">Chat</span>
      </router-link>
      <router-link to="/agent" class="nav-item" active-class="active">
        <el-icon :size="20"><Headset /></el-icon>
        <span class="nav-label">Agent</span>
      </router-link>
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <el-icon :size="20"><DataAnalysis /></el-icon>
        <span class="nav-label">Dashboard</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="user-section">
        <div class="user-avatar">
          {{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
        </div>
        <div class="user-info" v-if="expanded">
          <div class="user-name">{{ authStore.user?.username || 'User' }}</div>
          <div class="user-tenant">{{ authStore.user?.tenant_id || 'default' }}</div>
        </div>
      </div>
      <el-button
        class="logout-btn"
        :icon="SwitchButton"
        text
        @click="handleLogout"
        :title="'退出登录'"
      >
        <span v-if="expanded">退出</span>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChatDotRound,
  Headset,
  DataAnalysis,
  SwitchButton,
  ArrowLeft,
  ArrowRight,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const expanded = ref(true)

const expandIcon = computed(() => (expanded.value ? ArrowLeft : ArrowRight))

function toggle() {
  expanded.value = !expanded.value
}

function handleLogout() {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.sidebar-nav {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 64px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: width var(--transition-slow);
  overflow: hidden;
}

.sidebar-nav.expanded {
  width: 220px;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  color: var(--coral-primary);
}

.sidebar-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-2) 0;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 16px;
  color: var(--text-secondary);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: all var(--transition-fast);
  white-space: nowrap;
  cursor: pointer;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.nav-item.active {
  color: var(--coral-primary);
  background: rgba(255, 107, 53, 0.08);
  border-left-color: var(--coral-primary);
  box-shadow: var(--shadow-glow-coral);
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.sidebar-nav.expanded .nav-label {
  opacity: 1;
}

.sidebar-footer {
  padding: var(--space-3) 12px;
  border-top: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.user-section {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--coral-primary), var(--purple-accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.user-info {
  overflow: hidden;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.sidebar-nav.expanded .user-info {
  opacity: 1;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-tenant {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  width: 100%;
  justify-content: flex-start;
  color: var(--text-muted);
  padding: var(--space-2) 12px;
}

.logout-btn:hover {
  color: var(--danger);
}

.logout-btn .el-icon {
  margin-right: var(--space-2);
}
</style>
