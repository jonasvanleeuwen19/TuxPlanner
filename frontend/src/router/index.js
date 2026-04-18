import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import HomePage from '../views/HomePage.vue'
import CalendarPage from '../views/CalendarPage.vue'
import TodoPage from '../views/TodoPage.vue'
import IcalPage from '../views/IcalPage.vue'
import LoginPage from '../views/LoginPage.vue'

const routes = [
  { path: '/login', component: LoginPage, meta: { public: true } },
  { path: '/', component: HomePage },
  { path: '/calendar', component: CalendarPage },
  { path: '/todos', component: TodoPage },
  { path: '/ical', component: IcalPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const { isAuthenticated, authChecked, checkAuth } = useAuth()

  // Only verify the session once per page load
  if (!authChecked.value) {
    await checkAuth()
  }

  // Redirect unauthenticated users to login (preserve intended destination)
  if (!to.meta.public && !isAuthenticated.value) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Already logged-in users don't need to see the login page
  if (to.path === '/login' && isAuthenticated.value) {
    return { path: '/' }
  }
})

export default router
