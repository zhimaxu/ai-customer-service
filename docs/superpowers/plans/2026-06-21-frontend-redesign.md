# Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Full layout + visual overhaul of the Vue 3 frontend — dark coral-tech theme, unified collapsible sidebar navigation, animated login, and redesigned all four views.

**Architecture:** Introduce a global CSS variable theme system, a unified `App.vue` layout with `SidebarNav`, and a `ParticleBackground` canvas component. Refactor each view to remove its individual top-bar and adopt the dark coral palette. All animations use CSS transitions/transforms (no new npm packages).

**Tech Stack:** Vue 3 + Vite + Element Plus + ECharts + Pinia + Axios. Zero new dependencies.

---

## File Map

### New Files (6)
| File | Purpose |
|------|---------|
| `frontend/src/style.css` | Global CSS variables, base styles, transition classes |
| `frontend/src/components/SidebarNav.vue` | Collapsible left navigation (icons → text) |
| `frontend/src/components/ParticleBackground.vue` | Canvas particle network for login |
| `frontend/src/components/DarkCard.vue` | Reusable dark glassmorphism card |
| `frontend/src/components/StatusDot.vue` | Pulsing status indicator |
| `frontend/src/components/SkeletonLoader.vue` | Shimmer loading placeholder |

### Modified Files (13)
| File | Changes |
|------|---------|
| `frontend/src/main.js` | Import `style.css` |
| `frontend/src/App.vue` | Unified layout with SidebarNav + router-view |
| `frontend/src/router/index.js` | Add page transition wrapper |
| `frontend/src/views/Login.vue` | Particle background + frosted glass card + coral form |
| `frontend/src/views/ChatView.vue` | Remove top-bar, adjust layout |
| `frontend/src/views/AgentView.vue` | Remove top-bar, adjust layout |
| `frontend/src/views/DashboardView.vue` | Remove top-bar/nav-tabs, dark glass cards, ECharts dark theme |
| `frontend/src/components/MessageBubble.vue` | Coral gradient bg, spring animation, glow cursor |
| `frontend/src/components/AgentMessageBubble.vue` | Dark theme color mapping |
| `frontend/src/components/ChatWindow.vue` | Dark input area, coral send button |
| `frontend/src/components/SessionList.vue` | Dark cards, status dots |
| `frontend/src/components/AgentSidebar.vue` | Dark cards, status dots, unread badges |
| `frontend/src/components/AgentChat.vue` | Coral action buttons, quick reply pills |
| `frontend/src/components/TypingIndicator.vue` | Coral wave dots |
| `frontend/src/components/SettingsPanel.vue` | Dark theme drawer |
| `frontend/src/components/FileUpload.vue` | Coral dashed border |

---

## Phase 1: Foundation

### Task 1: Create Global CSS Variables and Base Styles

**Files:**
- Create: `frontend/src/style.css`

- [ ] **Step 1: Create `frontend/src/style.css` with all theme tokens**

```css
/* frontend/src/style.css */

:root {
  /* Backgrounds */
  --bg-deep: #0f1117;
  --bg-surface: #1a1d27;
  --bg-elevated: #232733;
  --bg-input: #161922;

  /* Brand */
  --coral-primary: #FF6B35;
  --coral-light: #FF8F66;
  --coral-dark: #E55A28;
  --purple-accent: #7C5CFC;
  --purple-light: #9B82FC;

  /* Text */
  --text-primary: #EAEAEA;
  --text-secondary: #9CA3AF;
  --text-muted: #6B7280;
  --text-inverse: #FFFFFF;

  /* Semantic */
  --success: #34D399;
  --warning: #FBBF24;
  --danger: #EF4444;

  /* Borders */
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-medium: rgba(255, 255, 255, 0.1);

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-glow-coral: 0 0 16px rgba(255, 107, 53, 0.25);
  --shadow-glow-purple: 0 0 16px rgba(124, 92, 252, 0.25);
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
  --shadow-card-hover: 0 8px 32px rgba(0, 0, 0, 0.4);

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.25s ease;
  --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reset & Base */
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--bg-deep);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Scrollbar — dark theme */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border-medium);
  border-radius: var(--radius-full);
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* Glassmorphism utility */
.glass {
  background: rgba(26, 29, 39, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
}

/* Fade-slide page transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity var(--transition-base), transform var(--transition-base);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Skeleton shimmer */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-surface) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

/* Dot grid pattern for chat areas */
.dot-grid-bg {
  background-image: radial-gradient(var(--border-subtle) 1px, transparent 1px);
  background-size: 24px 24px;
}
```

- [ ] **Step 2: Import `style.css` in `frontend/src/main.js`**

Read `frontend/src/main.js`, then add the import at the top:

```js
import '../src/style.css'
```

The full `main.js` should look like:

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import '../src/style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

- [ ] **Step 3: Verify the dev server starts without errors**

Run: `cd frontend && npm run dev`
Expected: Vite starts on port 5173, no compilation errors. The app should look exactly the same as before (no visual changes yet — this is just the foundation).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/style.css frontend/src/main.js
git commit -m "chore: add global CSS variables and base theme system"
```

---

### Task 2: Create SidebarNav Component

**Files:**
- Create: `frontend/src/components/SidebarNav.vue`

- [ ] **Step 1: Create `frontend/src/components/SidebarNav.vue`**

```vue
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
```

- [ ] **Step 2: Verify SidebarNav renders correctly**

Navigate to `/`, `/agent`, `/dashboard` — the sidebar should appear on the left with three nav items. Click the arrow icon to collapse/expand. The active route should have a coral left border and glow.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SidebarNav.vue
git commit -m "feat: add collapsible sidebar navigation component"
```

---

### Task 3: Refactor App.vue to Unified Layout

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Replace `frontend/src/App.vue`**

```vue
<template>
  <router-view v-slot="{ Component }">
    <transition name="fade-slide" mode="out-in">
      <div class="app-layout">
        <SidebarNav />
        <main class="app-main">
          <component :is="Component" />
        </main>
      </div>
    </transition>
  </router-view>
</template>

<script setup>
import SidebarNav from './components/SidebarNav.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  margin-left: 64px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-deep);
  transition: margin-left var(--transition-slow);
  min-height: 100vh;
}

.sidebar-nav.expanded ~ .app-main {
  margin-left: 220px;
}
</style>
```

Wait — the above CSS won't work because `SidebarNav` is inside the router-view slot, not a sibling. Fix with a wrapper approach:

```vue
<template>
  <div class="app-layout">
    <SidebarNav />
    <transition name="fade-slide" mode="out-in">
      <main class="app-main">
        <router-view />
      </main>
    </transition>
  </div>
</template>

<script setup>
import SidebarNav from './components/SidebarNav.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  margin-left: 64px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-deep);
  transition: margin-left var(--transition-slow);
  min-height: 100vh;
  overflow: auto;
}
</style>
```

- [ ] **Step 2: Verify layout**

All three views (Chat, Agent, Dashboard) should now share the same sidebar. The main content area should fill the remaining space. No top-bars visible yet — those will be removed next.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: unify app layout with sidebar and page transitions"
```

---

### Task 4: Add Page Transition to Router

**Files:**
- Modify: `frontend/src/router/index.js`

- [ ] **Step 1: Wrap route components with transition**

Read the current `frontend/src/router/index.js`. The transitions are already handled in `App.vue` with `<transition name="fade-slide">` wrapping `<router-view />`, so no router changes needed. Just verify the router file is unchanged and commit.

Actually, let's add a route-level meta for the transition:

```js
import { createRouter, createWebHistory } from 'vue-router'
import AgentView from '../views/AgentView.vue'
import DashboardView from '../views/DashboardView.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, transition: 'none' },
  },
  {
    path: '/',
    name: 'Chat',
    component: () => import('../views/ChatView.vue'),
    meta: { requiresAuth: true, transition: 'fade-slide' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, transition: 'fade-slide' },
  },
  {
    path: '/agent',
    name: 'Agent',
    component: AgentView,
    meta: { requiresAuth: true, transition: 'fade-slide' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth !== false && !authStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/router/index.js
git commit -m "chore: add transition meta to router routes"
```

---

## Phase 2: Login Page

### Task 5: Create ParticleBackground Component

**Files:**
- Create: `frontend/src/components/ParticleBackground.vue`

- [ ] **Step 1: Create `frontend/src/components/ParticleBackground.vue`**

```vue
<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
let animationId = null
let particles = []

const PARTICLE_COUNT = 70
const CONNECTION_DISTANCE = 150
const MOUSE_RADIUS = 120

class Particle {
  constructor(w, h) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * 0.6
    this.vy = (Math.random() - 0.5) * 0.6
    this.radius = Math.random() * 1.5 + 0.5
    this.opacity = Math.random() * 0.5 + 0.3
    this.pulseSpeed = Math.random() * 0.02 + 0.005
    this.pulseOffset = Math.random() * Math.PI * 2
  }

  update(time, w, h) {
    this.x += this.vx
    this.y += this.vy

    if (this.x < 0 || this.x > w) this.vx *= -1
    if (this.y < 0 || this.y > h) this.vy *= -1

    this.currentOpacity = this.opacity * (0.7 + 0.3 * Math.sin(time * this.pulseSpeed + this.pulseOffset))
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(255, 107, 53, ${this.currentOpacity})`
    ctx.fill()
  }
}

function init(canvas) {
  const w = (canvas.width = canvas.offsetWidth)
  const h = (canvas.height = canvas.offsetHeight)
  particles = []
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new Particle(w, h))
  }
}

function drawConnections(ctx, w, h, time) {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < CONNECTION_DISTANCE) {
        const alpha = (1 - dist / CONNECTION_DISTANCE) * 0.15
        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.strokeStyle = `rgba(255, 107, 53, ${alpha})`
        ctx.lineWidth = 0.5
        ctx.stroke()
      }
    }
  }
}

function animate(time) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = canvas.width
  const h = canvas.height

  ctx.clearRect(0, 0, w, h)

  particles.forEach((p) => {
    p.update(time, w, h)
    p.draw(ctx)
  })

  drawConnections(ctx, w, h, time)

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  init(canvas)
  window.addEventListener('resize', () => init(canvas))
  animationId = requestAnimationFrame(animate)
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
</style>
```

- [ ] **Step 2: Verify particles render**

Temporarily import and use the component in `Login.vue` to test. It should show 70 orange dots connected by faint lines on a transparent canvas.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ParticleBackground.vue
git commit -m "feat: add canvas particle network background component"
```

---

### Task 6: Redesign Login Page

**Files:**
- Modify: `frontend/src/views/Login.vue`

- [ ] **Step 1: Replace `frontend/src/views/Login.vue`**

```vue
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
```

- [ ] **Step 2: Visit `/login` and verify**

Login page should show: dark background, animated particle network, centered frosted glass card with coral logo icon, gradient title text, dark inputs with coral focus ring, coral gradient login button.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Login.vue frontend/src/components/ParticleBackground.vue
git commit -m "feat: redesign login page with particle background and coral theme"
```

---

## Phase 3: Chat View

### Task 7: Redesign MessageBubble

**Files:**
- Modify: `frontend/src/components/MessageBubble.vue`

- [ ] **Step 1: Replace `frontend/src/components/MessageBubble.vue`**

```vue
<template>
  <div class="message-bubble" :class="[senderClass, { streaming }]">
    <div class="avatar" :class="senderClass">
      {{ avatarLetter }}
    </div>
    <div class="bubble-wrapper">
      <div class="bubble-content">
        <div class="bubble-text" v-html="formattedContent"></div>
        <div class="bubble-footer">
          <span class="bubble-time">{{ time }}</span>
          <span v-if="streaming" class="streaming-dot"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  sender: { type: String, default: 'user' },
  content: { type: String, default: '' },
  time: { type: String, default: '' },
  streaming: { type: Boolean, default: false },
})

const avatarLetter = computed(() => {
  if (props.sender === 'user') return 'U'
  return 'AI'
})

const senderClass = computed(() => `msg-${props.sender}`)

const formattedContent = computed(() => {
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
})
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  align-items: flex-start;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.msg-user {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.msg-user .avatar {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  box-shadow: var(--shadow-glow-coral);
}

.msg-assistant .avatar {
  background: linear-gradient(135deg, var(--purple-accent), var(--purple-light));
  box-shadow: var(--shadow-glow-purple);
}

.bubble-wrapper {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.msg-user .bubble-wrapper {
  align-items: flex-end;
}

.bubble-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bubble-text {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.msg-user .bubble-text {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  color: var(--text-inverse);
  border-top-right-radius: var(--radius-sm);
}

.msg-assistant .bubble-text {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-top-left-radius: var(--radius-sm);
}

.bubble-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-end;
}

.bubble-time {
  font-size: 11px;
  color: var(--text-muted);
  font-family: SF Mono, Consolas, monospace;
}

.streaming-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--coral-primary);
  border-radius: 50%;
  animation: pulseDot 1.2s infinite ease-in-out;
}

@keyframes pulseDot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
```

- [ ] **Step 2: Verify message appearance**

In ChatView, user messages should have coral gradient bubbles on the right, assistant messages should have dark elevated bubbles on the left with purple avatar. New messages should spring in with animation.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MessageBubble.vue
git commit -m "feat: redesign message bubble with coral theme and spring animation"
```

---

### Task 8: Redesign TypingIndicator

**Files:**
- Modify: `frontend/src/components/TypingIndicator.vue`

- [ ] **Step 1: Replace `frontend/src/components/TypingIndicator.vue`**

```vue
<template>
  <div class="typing-indicator">
    <div class="avatar avatar-ai">AI</div>
    <div class="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</template>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
}

.avatar-ai {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--purple-accent), var(--purple-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.typing-dots span {
  width: 7px;
  height: 7px;
  background: var(--coral-primary);
  border-radius: 50%;
  display: inline-block;
  animation: typingWave 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }

@keyframes typingWave {
  0%, 80%, 100% {
    transform: scale(0.5);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/TypingIndicator.vue
git commit -m "feat: redesign typing indicator with coral wave animation"
```

---

### Task 9: Redesign ChatWindow

**Files:**
- Modify: `frontend/src/components/ChatWindow.vue`

- [ ] **Step 1: Replace `frontend/src/components/ChatWindow.vue`**

```vue
<template>
  <div class="chat-window dot-grid-bg">
    <div class="messages-area" ref="messagesRef">
      <div v-if="messages.length === 0" class="welcome">
        <div class="welcome-icon">
          <el-icon :size="48"><ChatDotRound /></el-icon>
        </div>
        <h2>欢迎使用 AI 智能客服</h2>
        <p>选择或创建一个会话开始对话</p>
      </div>
      <MessageBubble
        v-for="(msg, idx) in messages"
        :key="msg.id || idx"
        :sender="msg.sender"
        :content="msg.content"
        :time="msg.time"
        :streaming="idx === messages.length - 1 && isStreaming"
      />
      <TypingIndicator v-if="isStreaming && messages.length === 0" />
    </div>

    <div class="input-area glass">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="sendMessage"
        class="dark-input"
      />
      <el-button
        type="primary"
        @click="sendMessage"
        :disabled="!inputText.trim()"
        class="coral-send-btn"
      >
        <el-icon><Promotion /></el-icon>
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { Promotion, ChatDotRound } from '@element-plus/icons-vue'
import { useSessionStore } from '../stores/session'
import MessageBubble from './MessageBubble.vue'
import TypingIndicator from './TypingIndicator.vue'

const sessionStore = useSessionStore()
const inputText = ref('')
const messagesRef = ref(null)
const isStreaming = ref(false)

const messages = computed(() => sessionStore.messages)

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(() => sessionStore.messages.length, scrollToBottom)

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return

  const userMsg = {
    sender: 'user',
    content: text,
    time: new Date().toLocaleTimeString(),
  }
  sessionStore.addMessage(userMsg)
  inputText.value = ''
  scrollToBottom()

  isStreaming.value = true
  scrollToBottom()

  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        user_id: sessionStore.currentSession?.user_id || 'current-user',
        session_id: sessionStore.currentSession?.id,
        tenant_id: 'default',
      }),
    })

    if (!resp.ok) throw new Error('HTTP ' + resp.status)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let assistantContent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const events = buffer.split('\n\n')
      buffer = events.pop()

      for (const event of events) {
        const lines = event.split('\n')
        let eventType = 'data'
        let dataStr = ''

        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7)
          else if (line.startsWith('data: ')) dataStr = line.slice(6)
        }

        if (eventType === 'chunk' && dataStr) {
          const parsed = JSON.parse(dataStr)
          assistantContent += parsed.content || ''
          const lastMsg = sessionStore.messages[sessionStore.messages.length - 1]
          if (lastMsg && lastMsg.sender === 'assistant') {
            lastMsg.content = assistantContent
          } else {
            sessionStore.addMessage({
              sender: 'assistant',
              content: assistantContent,
              time: new Date().toLocaleTimeString(),
            })
          }
          scrollToBottom()
        } else if (eventType === 'done' && dataStr) {
          const parsed = JSON.parse(dataStr)
          if (sessionStore.currentSession?.id !== parsed.session_id) {
            sessionStore.currentSession = { id: parsed.session_id }
          }
        } else if (eventType === 'error' && dataStr) {
          const parsed = JSON.parse(dataStr)
          sessionStore.addMessage({
            sender: 'assistant',
            content: '出错了: ' + parsed.detail,
            time: new Date().toLocaleTimeString(),
          })
        }
      }
    }
  } catch (error) {
    sessionStore.addMessage({
      sender: 'assistant',
      content: '发送失败: ' + error.message,
      time: new Date().toLocaleTimeString(),
    })
  } finally {
    isStreaming.value = false
  }
}
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.welcome {
  text-align: center;
  padding: var(--space-16) var(--space-6);
  color: var(--text-muted);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto var(--space-4);
  background: linear-gradient(135deg, var(--coral-primary), var(--purple-accent));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-glow-coral);
}

.welcome h2 {
  font-size: 22px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 var(--space-2) 0;
}

.welcome p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.input-area {
  padding: var(--space-3) var(--space-4);
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
  border-top: 1px solid var(--border-subtle);
}

.input-area .el-textarea {
  flex: 1;
}

:deep(.dark-input .el-textarea__inner) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
}

:deep(.dark-input .el-textarea__inner:focus) {
  border-color: var(--coral-primary) !important;
  box-shadow: 0 0 0 1px var(--coral-primary) !important;
}

.coral-send-btn {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light)) !important;
  border: none !important;
  color: white !important;
  border-radius: var(--radius-md) !important;
  padding: 0 var(--space-4) !important;
  font-weight: 600 !important;
  box-shadow: var(--shadow-glow-coral);
  transition: all var(--transition-base);
  white-space: nowrap;
}

.coral-send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 24px rgba(255, 107, 53, 0.4) !important;
}

.coral-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/ChatWindow.vue
git commit -m "feat: redesign chat window with dark theme and coral input"
```

---

### Task 10: Redesign ChatView

**Files:**
- Modify: `frontend/src/views/ChatView.vue`

- [ ] **Step 1: Replace `frontend/src/views/ChatView.vue`**

```vue
<template>
  <div class="chat-view">
    <div class="main-area">
      <SessionList
        :current-session="sessionStore.currentSession"
        @select="handleSelectSession"
        @new="handleNewSession"
      />
      <ChatWindow />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useSessionStore } from '../stores/session'
import SessionList from '../components/SessionList.vue'
import ChatWindow from '../components/ChatWindow.vue'

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

.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
  margin-top: 0;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/ChatView.vue
git commit -m "refactor: remove top-bar from ChatView, use unified layout"
```

---

### Task 11: Redesign SessionList

**Files:**
- Modify: `frontend/src/components/SessionList.vue`

- [ ] **Step 1: Replace `frontend/src/components/SessionList.vue`**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/SessionList.vue frontend/src/components/StatusDot.vue
git commit -m "feat: redesign session list with dark cards and status indicators"
```

---

### Task 12: Create StatusDot Component

**Files:**
- Create: `frontend/src/components/StatusDot.vue`

- [ ] **Step 1: Create `frontend/src/components/StatusDot.vue`**

```vue
<template>
  <span class="status-dot" :class="statusClass" :title="statusLabel"></span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'active' },
})

const statusClass = computed(() => {
  const map = { active: 'online', human: 'busy', closed: 'offline' }
  return map[props.status] || 'offline'
})

const statusLabel = computed(() => {
  const map = { online: '活跃', busy: '人工服务', offline: '已关闭' }
  return map[statusClass.value] || '未知'
})
</script>

<style scoped>
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.online {
  background: var(--success);
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
  animation: pulse 2s infinite;
}

.status-dot.busy {
  background: var(--warning);
  box-shadow: 0 0 6px rgba(251, 191, 36, 0.5);
}

.status-dot.offline {
  background: var(--text-muted);
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.85); }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/StatusDot.vue
git commit -m "feat: add StatusDot component for session status indicators"
```

---

## Phase 4: Agent View

### Task 13: Redesign AgentSidebar

**Files:**
- Modify: `frontend/src/components/AgentSidebar.vue`

- [ ] **Step 1: Replace `frontend/src/components/AgentSidebar.vue`**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/AgentSidebar.vue
git commit -m "feat: redesign agent sidebar with dark theme and status indicators"
```

---

### Task 14: Redesign AgentMessageBubble

**Files:**
- Modify: `frontend/src/components/AgentMessageBubble.vue`

- [ ] **Step 1: Replace `frontend/src/components/AgentMessageBubble.vue`**

```vue
<template>
  <div class="message-bubble" :class="[senderClass]">
    <div class="avatar" :class="avatarClass">{{ avatarLetter }}</div>
    <div class="bubble-wrapper">
      <div class="bubble-content">
        <div class="bubble-text" v-html="formattedContent"></div>
        <div class="bubble-time">{{ time }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  sender: { type: String, default: 'user' },
  content: { type: String, default: '' },
  time: { type: String, default: '' },
})

const avatarLetter = computed(() => {
  if (props.sender === 'user') return 'U'
  if (props.sender === 'agent') return 'A'
  return 'AI'
})

const avatarClass = computed(() => {
  if (props.sender === 'user') return 'avatar-user'
  if (props.sender === 'agent') return 'avatar-agent'
  return 'avatar-assistant'
})

const senderClass = computed(() => {
  const map = { user: 'msg-left', agent: 'msg-left', assistant: 'msg-right' }
  return map[props.sender] || 'msg-left'
})

const formattedContent = computed(() => {
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
})
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  align-items: flex-start;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-left { flex-direction: row; }
.msg-right { flex-direction: row-reverse; }

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.avatar-user {
  background: linear-gradient(135deg, var(--text-muted), var(--text-secondary));
}

.avatar-agent {
  background: linear-gradient(135deg, var(--success), #6EE7B7);
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.3);
}

.avatar-assistant {
  background: linear-gradient(135deg, var(--purple-accent), var(--purple-light));
  box-shadow: var(--shadow-glow-purple);
}

.bubble-wrapper {
  max-width: 70%;
}

.msg-right .bubble-wrapper {
  align-self: flex-end;
}

.bubble-text {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.msg-left .bubble-text {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-top-left-radius: var(--radius-sm);
}

.msg-right .bubble-text {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light));
  color: var(--text-inverse);
  border-top-right-radius: var(--radius-sm);
}

.bubble-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  font-family: SF Mono, Consolas, monospace;
}

.msg-left .bubble-time { text-align: left; }
.msg-right .bubble-time { text-align: right; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/AgentMessageBubble.vue
git commit -m "feat: redesign agent message bubbles with dark theme"
```

---

### Task 15: Redesign AgentChat

**Files:**
- Modify: `frontend/src/components/AgentChat.vue`

- [ ] **Step 1: Replace `frontend/src/components/AgentChat.vue`**

```vue
<template>
  <div class="agent-chat">
    <div class="chat-header" v-if="sessionId">
      <div class="header-info">
        <span class="header-title">会话: {{ sessionId.slice(0, 8) }}...</span>
        <StatusDot status="active" />
      </div>
      <div class="header-actions">
        <el-button size="small" :icon="Camera" @click="handleTakeover" :disabled="isTakenOver" class="coral-sm-btn">
          转人工
        </el-button>
        <el-button size="small" type="danger" @click="handleClose" plain>关闭</el-button>
      </div>
    </div>
    <div class="chat-header" v-else>
      <span class="placeholder">请选择一个会话</span>
    </div>

    <div class="messages-area" ref="messagesRef">
      <div v-if="messages.length === 0 && sessionId" class="empty-messages">
        <el-icon :size="32"><ChatLineRound /></el-icon>
        <p>暂无消息</p>
      </div>
      <AgentMessageBubble
        v-for="(msg, idx) in messages"
        :key="idx"
        :sender="msg.sender"
        :content="msg.content"
        :time="msg.time"
      />
    </div>

    <!-- Quick reply bar -->
    <div class="quick-reply-bar" v-if="sessionId">
      <span class="quick-label">快捷回复:</span>
      <el-button
        v-for="(reply, idx) in quickReplies"
        :key="idx"
        size="small"
        @click="handleQuickReply(reply)"
        class="quick-pill"
      >
        {{ reply.substring(0, 12) }}{{ reply.length > 12 ? '...' : '' }}
      </el-button>
    </div>

    <div class="input-area glass" v-if="sessionId">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        placeholder="输入回复... (Ctrl+Enter 发送)"
        @keydown.ctrl.enter="sendMessage"
        class="dark-input"
      />
      <el-button type="primary" @click="sendMessage" :disabled="!inputText.trim()" class="coral-send-btn">
        <el-icon><Promotion /></el-icon>
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Promotion, Camera, ChatLineRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAgentStore } from '../stores/agent'
import AgentMessageBubble from './AgentMessageBubble.vue'
import StatusDot from './StatusDot.vue'

const props = defineProps({
  sessionId: String,
})

const agentStore = useAgentStore()
const inputText = ref('')
const messagesRef = ref(null)
const messages = ref([])
const isTakenOver = ref(false)

const quickReplies = computed(() => agentStore.quickReplies)

watch(() => props.sessionId, async (newId) => {
  if (newId) {
    isTakenOver.value = false
    try {
      const data = await agentStore.fetchSessionMessages(newId)
      messages.value = (data || []).map((m) => ({
        sender: m.sender || 'assistant',
        content: m.content || m.message || '',
        time: m.created_at ? new Date(m.created_at).toLocaleTimeString() : '',
      }))
      scrollToBottom()
    } catch (e) {
      console.error('Failed to fetch messages:', e)
    }
    agentStore.connectToSession(newId)
  }
})

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || !props.sessionId) return

  messages.value.push({
    sender: 'agent',
    content: text,
    time: new Date().toLocaleTimeString(),
  })
  inputText.value = ''
  scrollToBottom()

  try {
    await agentStore.replyToSession(props.sessionId, text)
  } catch (error) {
    ElMessage.error('发送失败: ' + error)
  }
}

async function handleQuickReply(content) {
  if (!props.sessionId) return
  messages.value.push({
    sender: 'agent',
    content,
    time: new Date().toLocaleTimeString(),
  })
  scrollToBottom()

  try {
    await agentStore.quickReplyToSession(props.sessionId, content)
  } catch (error) {
    ElMessage.error('发送失败: ' + error)
  }
}

async function handleTakeover() {
  if (!props.sessionId) return
  try {
    await agentStore.takeoverSession(props.sessionId)
    isTakenOver.value = true
    ElMessage.success('已接管会话')
  } catch (error) {
    ElMessage.error('接管失败: ' + error)
  }
}

function handleClose() {
  if (!props.sessionId) return
  agentStore.closeSession(props.sessionId).then(() => {
    ElMessage.success('会话已关闭')
  })
}
</script>

<style scoped>
.agent-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-deep);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-surface);
}

.header-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.header-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.coral-sm-btn {
  background: var(--coral-primary) !important;
  border: none !important;
  color: white !important;
  border-radius: var(--radius-sm) !important;
  font-size: 12px !important;
  padding: 0 var(--space-3) !important;
}

.placeholder {
  color: var(--text-muted);
  font-size: 14px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
}

.empty-messages {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-16) 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.empty-messages p {
  margin: 0;
  font-size: 14px;
}

.quick-reply-bar {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  flex-wrap: wrap;
  background: var(--bg-surface);
  align-items: center;
}

.quick-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-right: var(--space-2);
  white-space: nowrap;
}

.quick-pill {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-subtle) !important;
  color: var(--text-secondary) !important;
  border-radius: var(--radius-full) !important;
  font-size: 12px !important;
  padding: 2px var(--space-3) !important;
  transition: all var(--transition-fast);
}

.quick-pill:hover {
  background: rgba(255, 107, 53, 0.1) !important;
  border-color: var(--coral-primary) !important;
  color: var(--coral-primary) !important;
}

.input-area {
  padding: var(--space-3) var(--space-4);
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
}

.input-area .el-textarea {
  flex: 1;
}

:deep(.dark-input .el-textarea__inner) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
}

:deep(.dark-input .el-textarea__inner:focus) {
  border-color: var(--coral-primary) !important;
  box-shadow: 0 0 0 1px var(--coral-primary) !important;
}

.coral-send-btn {
  background: linear-gradient(135deg, var(--coral-primary), var(--coral-light)) !important;
  border: none !important;
  color: white !important;
  border-radius: var(--radius-md) !important;
  padding: 0 var(--space-4) !important;
  font-weight: 600 !important;
  box-shadow: var(--shadow-glow-coral);
  transition: all var(--transition-base);
  white-space: nowrap;
}

.coral-send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 24px rgba(255, 107, 53, 0.4) !important;
}

.coral-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/AgentChat.vue
git commit -m "feat: redesign agent chat with coral actions and quick reply pills"
```

---

### Task 16: Redesign AgentView

**Files:**
- Modify: `frontend/src/views/AgentView.vue`

- [ ] **Step 1: Replace `frontend/src/views/AgentView.vue`**

```vue
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/AgentView.vue
git commit -m "refactor: remove top-bar from AgentView, use unified layout"
```

---

## Phase 5: Dashboard

### Task 17: Create DarkCard and SkeletonLoader Components

**Files:**
- Create: `frontend/src/components/DarkCard.vue`
- Create: `frontend/src/components/SkeletonLoader.vue`

- [ ] **Step 1: Create `frontend/src/components/DarkCard.vue`**

```vue
<template>
  <div class="dark-card" :class="{ hoverable }">
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>
    <div class="card-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  hoverable: { type: Boolean, default: true },
})
</script>

<style scoped>
.dark-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.dark-card.hoverable:hover {
  border-color: var(--border-medium);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

.card-header {
  padding: var(--space-4) var(--space-5) var(--space-3);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-body {
  padding: var(--space-5);
}
</style>
```

- [ ] **Step 2: Create `frontend/src/components/SkeletonLoader.vue`**

```vue
<template>
  <div class="skeleton-loader" :class="skeletonType">
    <div v-for="n in lines" :key="n" class="skeleton-line"></div>
  </div>
</template>

<script setup>
defineProps({
  lines: { type: Number, default: 3 },
  type: { type: String, default: 'text' },
})

const skeletonType = `skeleton-${props.type}`
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skeleton-line {
  height: 12px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-surface) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-line:last-child {
  width: 60%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/DarkCard.vue frontend/src/components/SkeletonLoader.vue
git commit -m "feat: add DarkCard and SkeletonLoader reusable components"
```

---

### Task 18: Redesign DashboardView

**Files:**
- Modify: `frontend/src/views/DashboardView.vue`

- [ ] **Step 1: Replace `frontend/src/views/DashboardView.vue`**

```vue
<template>
  <div class="dashboard-view">
    <div class="dashboard-toolbar">
      <h2 class="page-title">数据分析</h2>
      <div class="toolbar-right">
        <el-select v-model="period" size="default" @change="loadData" class="dark-select">
          <el-option label="今天" value="day" />
          <el-option label="本周" value="week" />
          <el-option label="本月" value="month" />
        </el-select>
        <el-button :icon="SwitchButton" @click="handleLogout" text class="logout-link">退出</el-button>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Overview Cards -->
      <div class="overview-grid">
        <div class="stat-card" v-for="card in statCards" :key="card.label">
          <div class="stat-icon" :style="{ background: card.gradient }">
            <el-icon :size="20"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <DarkCard>
          <template #header>对话趋势</template>
          <div ref="trendChartRef" class="chart-container"></div>
        </DarkCard>
        <DarkCard>
          <template #header>满意度分布</template>
          <div ref="satChartRef" class="chart-container"></div>
        </DarkCard>
      </div>

      <!-- Efficiency Row -->
      <DarkCard>
        <template #header>效率指标</template>
        <div class="efficiency-grid">
          <div class="eff-item">
            <div class="eff-value">{{ efficiency.avg_first_response_time || '--' }}<span class="eff-unit">s</span></div>
            <div class="eff-label">首次响应时间</div>
          </div>
          <div class="eff-divider"></div>
          <div class="eff-item">
            <div class="eff-value">{{ efficiency.avg_response_time || '--' }}<span class="eff-unit">s</span></div>
            <div class="eff-label">平均响应时间</div>
          </div>
          <div class="eff-divider"></div>
          <div class="eff-item">
            <div class="eff-value">{{ overview.resolution_rate }}<span class="eff-unit">%</span></div>
            <div class="eff-label">解决率</div>
          </div>
          <div class="eff-divider"></div>
          <div class="eff-item">
            <div class="eff-value">{{ overview.total_messages }}</div>
            <div class="eff-label">消息总数</div>
          </div>
        </div>
      </DarkCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { SwitchButton, DataBoard, Connection, Star, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { getOverview, getChatStats, getSatisfactionStats, getEfficiencyStats } from '../api/stats'
import DarkCard from '../components/DarkCard.vue'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()
const period = ref('day')
const trendChartRef = ref(null)
const satChartRef = ref(null)

const overview = reactive({
  total_sessions: 0,
  active_sessions: 0,
  avg_satisfaction: 0,
  resolution_rate: 0,
  total_messages: 0,
})

const efficiency = reactive({
  avg_first_response_time: null,
  avg_response_time: null,
  resolution_rate: 0,
  total_messages: 0,
})

const statCards = [
  {
    label: '总会话数',
    value: '0',
    icon: 'Connection',
    gradient: 'linear-gradient(135deg, #FF6B35, #FF8F66)',
  },
  {
    label: '活跃会话',
    value: '0',
    icon: 'TrendCharts',
    gradient: 'linear-gradient(135deg, #34D399, #6EE7B7)',
  },
  {
    label: '平均满意度',
    value: '0/5',
    icon: 'Star',
    gradient: 'linear-gradient(135deg, #7C5CFC, #9B82FC)',
  },
  {
    label: '解决率',
    value: '0%',
    icon: 'DataBoard',
    gradient: 'linear-gradient(135deg, #FBBF24, #FCD34D)',
  },
]

let trendChart = null
let satChart = null

const CHART_COLORS = {
  coral: '#FF6B35',
  coralLight: '#FF8F66',
  purple: '#7C5CFC',
  green: '#34D399',
  warning: '#FBBF24',
  danger: '#EF4444',
  grid: 'rgba(255, 255, 255, 0.06)',
  axis: 'rgba(255, 255, 255, 0.3)',
  text: '#9CA3AF',
}

async function loadData() {
  try {
    const [overviewData, chatData, satData, effData] = await Promise.all([
      getOverview(),
      getChatStats(period.value),
      getSatisfactionStats(),
      getEfficiencyStats(),
    ])

    Object.assign(overview, {
      total_sessions: overviewData.total_sessions,
      active_sessions: overviewData.active_sessions,
      avg_satisfaction: overviewData.avg_satisfaction,
      resolution_rate: overviewData.resolution_rate,
      total_messages: overviewData.total_messages,
    })

    Object.assign(efficiency, effData)

    // Update stat card values
    statCards[0].value = overview.total_sessions.toLocaleString()
    statCards[1].value = overview.active_sessions.toLocaleString()
    statCards[2].value = `${overview.avg_satisfaction}/5`
    statCards[3].value = `${overview.resolution_rate}%`

    // Trend chart
    if (trendChartRef.value) {
      if (!trendChart) trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(26, 29, 39, 0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          textStyle: { color: '#EAEAEA' },
        },
        legend: {
          data: ['总计', '活跃', '已关闭'],
          textStyle: { color: CHART_COLORS.text },
          top: 0,
        },
        grid: { left: 40, right: 20, top: 40, bottom: 24 },
        xAxis: {
          type: 'category',
          data: chatData.trend.map((t) => t.date),
          axisLine: { lineStyle: { color: CHART_COLORS.grid } },
          axisLabel: { color: CHART_COLORS.text },
          axisTick: { show: false },
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisLabel: { color: CHART_COLORS.text },
          splitLine: { lineStyle: { color: CHART_COLORS.grid } },
        },
        series: [
          {
            name: '总计',
            type: 'line',
            smooth: true,
            data: chatData.trend.map((t) => t.total),
            itemStyle: { color: CHART_COLORS.coral },
            lineStyle: { width: 2.5 },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(255, 107, 53, 0.3)' },
                { offset: 1, color: 'rgba(255, 107, 53, 0.02)' },
              ]),
            },
          },
          {
            name: '活跃',
            type: 'line',
            smooth: true,
            data: chatData.trend.map((t) => t.active),
            itemStyle: { color: CHART_COLORS.green },
            lineStyle: { width: 2 },
          },
          {
            name: '已关闭',
            type: 'line',
            smooth: true,
            data: chatData.trend.map((t) => t.closed),
            itemStyle: { color: CHART_COLORS.warning },
            lineStyle: { width: 2 },
          },
        ],
      })
    }

    // Satisfaction chart
    if (satChartRef.value) {
      if (!satChart) satChart = echarts.init(satChartRef.value)
      const dist = satData.distribution
      satChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(26, 29, 39, 0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          textStyle: { color: '#EAEAEA' },
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          textStyle: { color: CHART_COLORS.text },
        },
        series: [
          {
            name: '满意度',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 6,
              borderColor: 'rgba(15, 17, 23, 0.8)',
              borderWidth: 2,
            },
            label: {
              show: true,
              formatter: '{b}: {c}',
              color: CHART_COLORS.text,
            },
            data: [
              { value: dist['5'] || 0, name: '5 星', itemStyle: { color: CHART_COLORS.coral } },
              { value: dist['4'] || 0, name: '4 星', itemStyle: { color: CHART_COLORS.coralLight } },
              { value: dist['3'] || 0, name: '3 星', itemStyle: { color: CHART_COLORS.warning } },
              { value: dist['2'] || 0, name: '2 星', itemStyle: { color: '#F87171' } },
              { value: dist['1'] || 0, name: '1 星', itemStyle: { color: CHART_COLORS.danger } },
            ],
          },
        ],
      })
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

function handleLogout() {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    trendChart?.resize()
    satChart?.resize()
  })
})
</script>

<style scoped>
.dashboard-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-deep);
}

.dashboard-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-surface);
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.logout-link {
  color: var(--text-muted) !important;
  font-size: 13px;
}

.logout-link:hover {
  color: var(--danger) !important;
}

:deep(.dark-select .el-input__wrapper) {
  background-color: var(--bg-input) !important;
  border-color: var(--border-subtle) !important;
  box-shadow: none !important;
  border-radius: var(--radius-md) !important;
}

:deep(.dark-select .el-input__inner) {
  color: var(--text-primary) !important;
}

:deep(.dark-select .el-input__wrapper.is-focus) {
  border-color: var(--coral-primary) !important;
}

:deep(.dark-select .el-select__placeholder) {
  color: var(--text-primary) !important;
}

:deep(.dark-select .el-input__suffix-icon) {
  color: var(--text-muted) !important;
}

.dashboard-content {
  flex: 1;
  padding: var(--space-6);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: var(--border-medium);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.chart-container {
  height: 300px;
}

.efficiency-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-6);
  padding: var(--space-4) 0;
}

.eff-item {
  text-align: center;
}

.eff-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--coral-primary);
  line-height: 1.2;
}

.eff-unit {
  font-size: 16px;
  font-weight: 400;
  color: var(--text-muted);
  margin-left: 2px;
}

.eff-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: var(--space-2);
}

.eff-divider {
  width: 1px;
  background: var(--border-subtle);
  align-self: stretch;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/DashboardView.vue frontend/src/components/DarkCard.vue
git commit -m "feat: redesign dashboard with dark theme, coral stat cards, and ECharts dark charts"
```

---

### Task 19: Redesign Remaining Components

**Files:**
- Modify: `frontend/src/components/SettingsPanel.vue`
- Modify: `frontend/src/components/FileUpload.vue`

- [ ] **Step 1: Replace `frontend/src/components/SettingsPanel.vue`**

```vue
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
```

- [ ] **Step 2: Replace `frontend/src/components/FileUpload.vue`**

```vue
<template>
  <div
    class="file-upload"
    @drop.prevent="handleDrop"
    @dragover.prevent
    @click="$refs.fileInput?.click()"
  >
    <el-tooltip content="拖拽或点击上传文件" placement="top">
      <el-button circle class="upload-btn">
        <el-icon :size="18"><Upload /></el-icon>
      </el-button>
    </el-tooltip>
    <input
      ref="fileInput"
      type="file"
      accept=".md,.txt,.csv,.pdf,.docx,.xlsx,.png,.jpg,.jpeg,.webp"
      style="display: none"
      @change="handleFile"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['uploaded'])
const fileInput = ref(null)

async function handleFile(event) {
  const file = event.target.files[0]
  if (!file) return
  await processFile(file)
}

async function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (!file) return
  await processFile(file)
}

async function processFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('tenant_id', 'default')

  try {
    const resp = await fetch('/api/knowledge/upload', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + localStorage.getItem('token') },
      body: formData,
    })
    const data = await resp.json()
    if (data.id) {
      ElMessage.success('文件上传成功')
      emit('uploaded', data.title)
    }
  } catch (error) {
    ElMessage.error('上传失败: ' + error)
  }
}
</script>

<style scoped>
.upload-btn {
  background: var(--bg-elevated) !important;
  border: 1px dashed var(--border-medium) !important;
  color: var(--text-secondary) !important;
  transition: all var(--transition-fast);
}

.upload-btn:hover {
  border-color: var(--coral-primary) !important;
  color: var(--coral-primary) !important;
  box-shadow: var(--shadow-glow-coral);
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SettingsPanel.vue frontend/src/components/FileUpload.vue
git commit -m "feat: apply dark theme to SettingsPanel and FileUpload components"
```

---

### Task 20: Final Polish — AgentView Layout Fix

**Files:**
- Modify: `frontend/src/views/AgentView.vue`

- [ ] **Step 1: Ensure AgentView has correct layout with resizable panels**

The AgentView already has the correct structure from Task 16. Just verify and commit.

```bash
git add frontend/src/views/AgentView.vue
git commit -m "chore: finalize AgentView unified layout"
```

---

## Phase 6: Verification

### Task 21: End-to-End Verification

- [ ] **Step 1: Start dev server and visit all routes**

```bash
cd frontend && npm run dev
```

Visit each page and verify:
- `/login` — Particle animation, frosted glass card, coral gradient button, dark inputs
- `/` (Chat) — SidebarNav on left, session list with dark cards, chat area with dot grid, coral user bubbles
- `/agent` (Agent) — SidebarNav, dark session list with status dots, agent chat with coral actions
- `/dashboard` (Dashboard) — SidebarNav, coral stat cards with icons, dark ECharts, efficiency grid

- [ ] **Step 2: Test interactions**

- Collapse/expand sidebar — smooth width transition
- Navigate between pages — fade-slide transition
- Login form — coral focus ring on inputs
- Send a message (if backend running) — coral bubble appears with spring animation
- Dashboard period selector — coral underline highlight

- [ ] **Step 3: Check responsive behavior**

Resize browser window. All layouts should adapt. Charts should resize.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: verify all redesigned pages work correctly"
```

---

## Summary

**Total tasks**: 21
**Total phases**: 6
**New files**: 6 (SidebarNav, ParticleBackground, DarkCard, SkeletonLoader, StatusDot, plus style.css)
**Modified files**: 14 (App.vue, main.js, router, 4 views, 8 components)
**Dependencies added**: 0
**Estimated effort**: 15-20 hours

**Order of execution**: Phase 1 → 2 → 3 → 4 → 5 → 6. Each task is self-contained and testable independently.
