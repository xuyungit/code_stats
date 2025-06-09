<template>
  <AppLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Repository Statistics</h1>
            <p v-if="repository" class="text-gray-600">{{ repository.name }}</p>
          </div>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedDays"
              @change="fetchStats"
              class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="7">Last 7 days</option>
              <option value="14">Last 14 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
            <RouterLink
              to="/repositories"
              class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
            >
              ← Back to Repositories
            </RouterLink>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8">
          <div class="text-gray-500">Loading statistics...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {{ error }}
        </div>

        <!-- Statistics Content -->
        <div v-else class="space-y-8">
          <!-- Period Summary -->
          <div v-if="periodStats" class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <span class="text-white text-sm font-medium">C</span>
                    </div>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Commits</dt>
                      <dd class="text-lg font-medium text-gray-900">{{ periodStats.commits_count }}</dd>
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
                      <span class="text-white text-sm font-medium">+</span>
                    </div>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Lines Added</dt>
                      <dd class="text-lg font-medium text-gray-900">{{ periodStats.added_lines }}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                      <span class="text-white text-sm font-medium">-</span>
                    </div>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Lines Deleted</dt>
                      <dd class="text-lg font-medium text-gray-900">{{ periodStats.deleted_lines }}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <span class="text-white text-sm font-medium">Δ</span>
                    </div>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Net Change</dt>
                      <dd class="text-lg font-medium text-gray-900">
                        {{ periodStats.added_lines - periodStats.deleted_lines }}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Daily Activity Chart -->
          <div v-if="dailyStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Daily Activity</h3>
            <div class="h-64">
              <canvas ref="dailyChart"></canvas>
            </div>
          </div>

          <!-- Author Breakdown -->
          <div v-if="authorStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Author Contributions</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Author
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Commits
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lines Added
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lines Deleted
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Net Change
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="author in authorStats" :key="author.author_email">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="flex-shrink-0 h-8 w-8">
                          <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                            <span class="text-xs font-medium text-gray-700">
                              {{ author.author_name.charAt(0).toUpperCase() }}
                            </span>
                          </div>
                        </div>
                        <div class="ml-4">
                          <div class="text-sm font-medium text-gray-900">{{ author.author_name }}</div>
                          <div class="text-sm text-gray-500">{{ author.author_email }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ author.commits_count }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                      +{{ author.added_lines }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                      -{{ author.deleted_lines }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ author.added_lines - author.deleted_lines }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useApi } from '@/composables/useApi'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface Repository {
  id: number
  name: string
  local_path: string
}

interface PeriodStats {
  commits_count: number
  added_lines: number
  deleted_lines: number
  total_files_changed: number
  authors_count: number
}

interface DailyStats {
  date: string
  commits_count: number
  added_lines: number
  deleted_lines: number
  total_files_changed: number
  authors_count: number
}

interface AuthorStats {
  author_email: string
  author_name: string
  commits_count: number
  added_lines: number
  deleted_lines: number
  total_files_changed: number
}

const route = useRoute()
const { api, loading, error } = useApi()

const repository = ref<Repository | null>(null)
const selectedDays = ref(7)
const periodStats = ref<PeriodStats | null>(null)
const dailyStats = ref<DailyStats[]>([])
const authorStats = ref<AuthorStats[]>([])
const dailyChart = ref<HTMLCanvasElement>()

const repoId = Number(route.params.id)

const fetchRepository = async () => {
  try {
    const response = await api.get(`/repositories/${repoId}`)
    repository.value = response.data
  } catch (err) {
    console.error('Failed to fetch repository:', err)
  }
}

const fetchStats = async () => {
  try {
    // Fetch period stats
    const periodResponse = await api.get(`/repositories/${repoId}/stats/period`, {
      params: { days: selectedDays.value }
    })
    periodStats.value = periodResponse.data

    // Fetch daily stats
    const dailyResponse = await api.get(`/repositories/${repoId}/stats/daily`, {
      params: { days: selectedDays.value }
    })
    dailyStats.value = dailyResponse.data

    // Fetch author stats
    const authorResponse = await api.get(`/repositories/${repoId}/stats/authors`, {
      params: { days: selectedDays.value }
    })
    authorStats.value = authorResponse.data

    // Update chart
    await nextTick()
    updateChart()
  } catch (err) {
    console.error('Failed to fetch statistics:', err)
  }
}

const updateChart = () => {
  if (!dailyChart.value || dailyStats.value.length === 0) return

  const ctx = dailyChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if ((dailyChart.value as any).chart) {
    (dailyChart.value as any).chart.destroy()
  }

  const labels = dailyStats.value.map(stat => 
    new Date(stat.date).toLocaleDateString()
  )

  const chart = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Lines Added',
          data: dailyStats.value.map(stat => stat.added_lines),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
        },
        {
          label: 'Lines Deleted',
          data: dailyStats.value.map(stat => stat.deleted_lines),
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
        },
        {
          label: 'Commits',
          data: dailyStats.value.map(stat => stat.commits_count),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Lines'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Commits'
          },
          grid: {
            drawOnChartArea: false,
          },
        }
      }
    }
  })

  // Store chart reference for cleanup
  ;(dailyChart.value as any).chart = chart
}

onMounted(async () => {
  await fetchRepository()
  await fetchStats()
})
</script>