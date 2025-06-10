import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export interface User {
  id: number
  email: string
  username: string
  created_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastActivity = ref<number>(Date.now())

  const isAuthenticated = computed(() => !!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = null
    localStorage.removeItem('token')
  }

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      loading.value = true
      error.value = null

      const response = await axios.post('/api/auth/login', credentials, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      setToken(response.data.access_token)
      await fetchUser()
      updateActivity()
      startActivityMonitoring()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (credentials: RegisterCredentials): Promise<boolean> => {
    try {
      loading.value = true
      error.value = null

      await axios.post('/api/auth/register', credentials)
      
      // Auto-login after registration
      return await login({
        username: credentials.username,
        password: credentials.password,
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const fetchUser = async (): Promise<void> => {
    if (!token.value) return

    try {
      const response = await axios.get('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      user.value = response.data
    } catch (err) {
      // Token might be invalid
      logout()
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    if (!token.value) return false

    try {
      const response = await axios.post('/api/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })
      
      setToken(response.data.access_token)
      updateActivity()
      return true
    } catch (err) {
      // Refresh failed, logout user
      logout()
      return false
    }
  }

  const updateActivity = () => {
    lastActivity.value = Date.now()
  }

  const shouldRefreshToken = (): boolean => {
    const now = Date.now()
    const timeSinceActivity = now - lastActivity.value
    // Refresh if more than 2 hours since last activity and still authenticated
    return isAuthenticated.value && timeSinceActivity > 2 * 60 * 60 * 1000
  }

  const logout = () => {
    stopActivityMonitoring()
    clearToken()
    user.value = null
    error.value = null
  }

  // Initialize user on store creation
  if (token.value) {
    fetchUser()
  }

  // Set up activity-based token refresh
  let refreshInterval: NodeJS.Timeout | null = null
  
  const startActivityMonitoring = () => {
    if (refreshInterval) return
    
    refreshInterval = setInterval(() => {
      if (shouldRefreshToken()) {
        refreshToken()
      }
    }, 30 * 60 * 1000) // Check every 30 minutes
  }

  const stopActivityMonitoring = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  // Start monitoring if authenticated
  if (isAuthenticated.value) {
    startActivityMonitoring()
  }

  return {
    token: computed(() => token.value),
    user: computed(() => user.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    refreshToken,
    updateActivity,
    startActivityMonitoring,
    stopActivityMonitoring,
  }
})