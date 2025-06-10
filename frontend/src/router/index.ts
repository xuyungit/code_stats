import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/repositories',
      name: 'repositories',
      component: () => import('../views/RepositoriesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/repositories/:id/stats',
      name: 'repository-stats',
      component: () => import('../views/RepositoryStatsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/authors',
      name: 'authors',
      component: () => import('../views/AuthorsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
