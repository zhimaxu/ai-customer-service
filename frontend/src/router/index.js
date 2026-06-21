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
