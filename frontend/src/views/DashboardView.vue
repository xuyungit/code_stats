<template>
  <AppLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Quick Stats Cards -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">R</span>
                  </div>
                </div>
                <div class="ml-8 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-semibold text-gray-700 truncate">
                      Total Repositories
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ repositories.length }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">A</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-semibold text-gray-700 truncate">
                      Analyzed Today
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ analyzedToday }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                    <span class="text-white text-sm font-medium">L</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-semibold text-gray-700 truncate">
                      Lines This Week
                    </dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ totalLinesThisWeek }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Repositories -->
        <div class="mt-12">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Repositories</h2>
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <ul role="list" class="divide-y divide-gray-200">
              <li v-for="repo in repositories.slice(0, 5)" :key="repo.id" class="px-8 py-6">
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span class="text-sm font-medium text-gray-700">
                          {{ repo.name.charAt(0).toUpperCase() }}
                        </span>
                      </div>
                    </div>
                    <div class="ml-6">
                      <div class="text-sm font-medium text-gray-900">{{ repo.name }}</div>
                      <div class="text-sm text-gray-500">{{ repo.local_path }}</div>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">
                      {{ repo.last_analyzed_at ? formatDate(repo.last_analyzed_at) : 'Never analyzed' }}
                    </span>
                    <RouterLink
                      :to="`/repositories/${repo.id}/stats`"
                      class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                    >
                      View Stats
                    </RouterLink>
                  </div>
                </div>
              </li>
              <li v-if="repositories.length === 0" class="px-6 py-4 text-center text-gray-500">
                No repositories yet. <RouterLink to="/repositories" class="text-indigo-600">Add your first repository</RouterLink>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useApi } from '@/composables/useApi'

interface Repository {
  id: number
  name: string
  local_path: string
  last_analyzed_at: string | null
}

const { api, loading, error } = useApi()
const repositories = ref<Repository[]>([])
const analyzedToday = ref(0)
const totalLinesThisWeek = ref(0)

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const fetchRepositories = async () => {
  try {
    const response = await api.get('/repositories/')
    repositories.value = response.data
  } catch (err) {
    console.error('Failed to fetch repositories:', err)
  }
}

const fetchDashboardStats = async () => {
  // Count analyzed today
  const today = new Date().toISOString().split('T')[0]
  analyzedToday.value = repositories.value.filter(repo => 
    repo.last_analyzed_at && repo.last_analyzed_at.startsWith(today)
  ).length

  // This is a simplified calculation - in a real app you'd call an API
  totalLinesThisWeek.value = repositories.value.length * 1234 // Mock data
}

onMounted(async () => {
  await fetchRepositories()
  await fetchDashboardStats()
})
</script>