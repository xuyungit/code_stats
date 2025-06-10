import axios from 'axios'
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = '/api'

export const useApi = () => {
  const authStore = useAuthStore()
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Add auth token to requests and track activity
  api.interceptors.request.use((config) => {
    const token = authStore.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      authStore.updateActivity() // Track user activity
    }
    return config
  })

  // Handle auth errors
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        authStore.logout()
      }
      return Promise.reject(error)
    }
  )

  const request = async <T>(requestFn: () => Promise<T>): Promise<T | null> => {
    try {
      loading.value = true
      error.value = null
      const result = await requestFn()
      return result
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'An error occurred'
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    api,
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    request,
  }
}