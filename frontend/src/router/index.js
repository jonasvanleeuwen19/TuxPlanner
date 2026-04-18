import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import HomePage from '../views/HomePage.vue'
import CalendarPage from '../views/CalendarPage.vue'
import TodoPage from '../views/TodoPage.vue'
import IcalPage from '../views/IcalPage.vue'
import LoginPage from '../views/LoginPage.vue'
import SetupPage from '../views/SetupPage.vue'

const routes = [
  { path: '/login', component: LoginPage, meta: { public: true } },
  { path: '/setup', component: SetupPage, meta: { public: true, setupOnly: true } },
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
  const { isAuthenticated, authChecked, setupRequired, setupChecked, checkAuth, checkSetup } = useAuth()

  // Check setup status once per page load
  if (!setupChecked.value) {
    await checkSetup()
  }

  // If setup hasn't been done, always redirect to /setup (except when already there)
  if (setupRequired.value) {
    if (to.path !== '/setup') {
      return { path: '/setup' }
    }
    return
  }

  // Setup is done – prevent access to /setup page
  if (to.meta.setupOnly) {
    return { path: '/' }
  }

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
