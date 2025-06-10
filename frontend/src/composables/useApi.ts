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

  // AI Statistics API methods
  const getAiCodingStats = async (repoId: number, days: number = 30) => {
    return request(() => api.get(`/repositories/${repoId}/stats/ai-coding?days=${days}`))
  }

  const getAiAuthorStats = async (repoId: number, days: number = 30) => {
    return request(() => api.get(`/repositories/${repoId}/stats/ai-authors?days=${days}`))
  }

  const getAiTrends = async (repoId: number, days: number = 30) => {
    return request(() => api.get(`/repositories/${repoId}/stats/ai-trends?days=${days}`))
  }

  const getOverallAiStats = async (days: number = 30) => {
    return request(() => api.get(`/stats/ai-coding?days=${days}`))
  }

  const getOverallAiTrends = async (days: number = 30) => {
    return request(() => api.get(`/stats/ai-trends?days=${days}`))
  }

  return {
    api,
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    request,
    // AI Statistics methods
    getAiCodingStats,
    getAiAuthorStats,
    getAiTrends,
    getOverallAiStats,
    getOverallAiTrends,
  }
}