import { ref } from 'vue'
import api from '../api/index.js'

// Module-level singletons so auth state is shared across all component instances
const isAuthenticated = ref(false)
const currentUser = ref(null)
const authChecked = ref(false)

export function useAuth() {
  /**
   * Verify the current session by calling /auth/me.
   * Sets isAuthenticated and currentUser accordingly.
   */
  async function checkAuth() {
    try {
      const { data } = await api.get('/auth/me')
      isAuthenticated.value = true
      currentUser.value = data
    } catch {
      isAuthenticated.value = false
      currentUser.value = null
    } finally {
      authChecked.value = true
    }
  }

  /**
   * Submit login credentials (form-encoded as required by OAuth2PasswordRequestForm).
   * On success the backend sets an httpOnly cookie automatically.
   */
  async function login(username, password) {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    await checkAuth()
  }

  /**
   * Log out by calling /auth/logout (which clears the httpOnly cookie server-side)
   * and resetting local auth state.
   */
  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {
      // Ignore errors – clear local state regardless
    }
    isAuthenticated.value = false
    currentUser.value = null
  }

  return { isAuthenticated, currentUser, authChecked, checkAuth, login, logout }
}
