<template>
  <div class="login-page">
    <ParticleBackground />

    <div class="login-card glass">
      <div class="card-header">
        <div class="logo-icon">
          <el-icon :size="32"><MagicStick /></el-icon>
        </div>
        <h1 class="logo-text">AI 智能客服</h1>
        <p class="subtitle">多模态 · 全天候 · 智能化</p>
      </div>

      <el-form :model="form" @submit.prevent="handleLogin" class="login-form">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
            class="dark-input"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            class="dark-input"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.tenant_id"
            placeholder="租户 ID（可选）"
            size="small"
            class="dark-input-small"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="loading"
            size="large"
            class="coral-btn"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import ParticleBackground from '../components/ParticleBackground.vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  tenant_id: 'default',
})

async function handleLogin() {
  loading.value = true
  try {
    const fakeToken = 'demo-token-' + Date.now()
    authStore.login(fakeToken, { username: form.username, tenant_id: form.tenant_id })
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败: ' + error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-deep);
  overflow: hidden;
}

.login-card {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: var(--space-10) var(--space-8);
  border-radius: var(--radius-xl);
  animation: cardEnter 0.6s ease-out;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.logo-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto var(--space-3);
  background: linear-gradient(135deg, var(--coral-primary), var(--purple-accent));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-glow-coral);
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Dark input overrides for Element Plus */
:deep(.dark-input .el-input__wrapper) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  box-shadow: none !important;
  border-radius: var(--radius-md) !important;
  padding: 4px 12px !important;
}

:deep(.dark-input .el-input__inner) {
  color: var(--text-primary) !important;
}

:deep(.dark-input .el-input__wrapper.is-focus) {
  border-color: var(--coral-primary) !important;
  box-shadow: 0 0 0 1px var(--coral-primary) !important;
}

:deep(.dark-input-small .el-input__wrapper) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  box-shadow: none !important;
  border-radius: var(--radius-md) !important;
}

:deep(.dark-input-small .el-input__inner) {
  color: var(--text-secondary) !important;
  font-size: 12px !important;
}

/* Coral gradient button */
:deep(.coral-btn) {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light)) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  letter-spacing: 4px !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-glow-coral);
  transition: all var(--transition-base);
}

:deep(.coral-btn:hover) {
  transform: translateY(-1px);
  box-shadow: 0 0 24px rgba(255, 107, 53, 0.4) !important;
}

:deep(.coral-btn:active) {
  transform: translateY(0);
}

:deep(.coral-btn .el-button__loading) {
  color: white;
}
</style>
