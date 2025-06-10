<template>
  <AppLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Repository Management</h1>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedDays"
              @change="fetchOverviewStats"
              class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="7">Last 7 days</option>
              <option value="14">Last 14 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
            <div class="flex space-x-3">
              <button
                @click="analyzeAllRepositories"
                :disabled="analyzingAll || repositories.length === 0"
                class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {{ analyzingAll ? 'Analyzing All...' : 'Analyze All' }}
              </button>
              <button
                @click="showAddForm = true"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Add Repository
              </button>
            </div>
          </div>
        </div>

        <!-- Overview Statistics Cards -->
        <div v-if="repositories.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <!-- Total Repositories -->
          <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-indigo-500 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-6 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Total Repositories
                    </dt>
                    <dd class="text-2xl font-bold text-gray-900">
                      {{ repositories.length }}
                    </dd>
                    <dd class="text-xs text-gray-400">{{ analyzedCount }} analyzed</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Total Activity Stats -->
          <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-6 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Total Commits
                    </dt>
                    <dd class="text-2xl font-bold text-gray-900">
                      {{ overviewStats?.total_commits?.toLocaleString() || '0' }}
                    </dd>
                    <dd class="text-xs text-gray-400">Last {{ selectedDays }} days</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Lines Added -->
          <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-6 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Lines Added
                    </dt>
                    <dd class="text-2xl font-bold text-green-600">
                      +{{ overviewStats?.total_added?.toLocaleString() || '0' }}
                    </dd>
                    <dd class="text-xs text-gray-400">Last {{ selectedDays }} days</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Net Change -->
          <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
            <div class="p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="{
                    'bg-green-500': netChange >= 0,
                    'bg-red-500': netChange < 0
                  }">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="netChange >= 0 ? 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6' : 'M13 17h8m0 0V9m0 8l-8-8-4 4-6-6'"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-6 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">
                      Net Change
                    </dt>
                    <dd class="text-2xl font-bold" :class="{
                      'text-green-600': netChange >= 0,
                      'text-red-600': netChange < 0
                    }">
                      {{ netChange >= 0 ? '+' : '' }}{{ netChange.toLocaleString() }}
                    </dd>
                    <dd class="text-xs text-gray-400">Last {{ selectedDays }} days</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Trends Chart -->
        <div v-if="repositories.length > 0 && dailyTrends.length > 0" class="bg-white p-6 rounded-lg shadow-lg border border-gray-200 mb-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Repository Activity Trends</h3>
          <div class="h-80">
            <canvas ref="trendsChart"></canvas>
          </div>
        </div>

        <!-- Add Repository Form -->
        <div v-if="showAddForm" class="mb-6 bg-white p-6 rounded-lg shadow">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add New Repository</h3>
          <form @submit.prevent="handleAddRepository" class="space-y-4">
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <input
                id="name"
                v-model="newRepo.name"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="My Project"
              />
            </div>
            <div>
              <label for="path" class="block text-sm font-medium text-gray-700">Local Path</label>
              <input
                id="path"
                v-model="newRepo.local_path"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="/path/to/your/git/repository"
              />
            </div>
            <div>
              <label for="description" class="block text-sm font-medium text-gray-700">Description (optional)</label>
              <textarea
                id="description"
                v-model="newRepo.description"
                rows="3"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Description of your repository"
              />
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="cancelAdd"
                class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="adding"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {{ adding ? 'Adding...' : 'Add Repository' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {{ error }}
        </div>

        <!-- Repositories List -->
        <div class="bg-white shadow overflow-hidden sm:rounded-md">
          <ul role="list" class="divide-y divide-gray-200">
            <li v-for="repo in repositories" :key="repo.id" class="px-8 py-6">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                      <span class="text-sm font-medium text-indigo-800">
                        {{ repo.name.charAt(0).toUpperCase() }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-6">
                    <div class="text-sm font-medium text-gray-900">{{ repo.name }}</div>
                    <div class="text-sm text-gray-500">{{ repo.local_path }}</div>
                    <div v-if="repo.description" class="text-sm text-gray-400">{{ repo.description }}</div>
                  </div>
                </div>
                <div class="flex items-center space-x-6">
                  <span class="text-sm text-gray-500">
                    {{ repo.last_analyzed_at ? `Last analyzed: ${formatDate(repo.last_analyzed_at)}` : 'Never analyzed' }}
                  </span>
                  <button
                    @click="analyzeRepository(repo.id)"
                    :disabled="analyzingRepo === repo.id"
                    class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                  >
                    {{ analyzingRepo === repo.id ? 'Analyzing...' : 'Analyze' }}
                  </button>
                  <RouterLink
                    :to="`/repositories/${repo.id}/stats`"
                    class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                  >
                    View Stats
                  </RouterLink>
                  <button
                    @click="deleteRepository(repo.id)"
                    :disabled="deletingRepo === repo.id"
                    class="text-red-600 hover:text-red-900 text-sm font-medium disabled:opacity-50"
                  >
                    {{ deletingRepo === repo.id ? 'Deleting...' : 'Delete' }}
                  </button>
                </div>
              </div>
            </li>
            <li v-if="repositories.length === 0" class="px-6 py-8 text-center text-gray-500">
              No repositories yet. Click "Add Repository" to get started.
            </li>
          </ul>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useApi } from '@/composables/useApi'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface Repository {
  id: number
  name: string
  local_path: string
  description?: string
  last_analyzed_at: string | null
}

interface OverviewStats {
  total_commits: number
  total_added: number
  total_deleted: number
  total_authors: number
  repositories_included: number[]
}

interface DailyTrend {
  date: string
  daily_stats: {
    author_id: number
    commits_count: number
    added_lines: number
    deleted_lines: number
    files_changed: number
  }[]
}

const { api, loading, error } = useApi()
const repositories = ref<Repository[]>([])
const showAddForm = ref(false)
const adding = ref(false)
const analyzingRepo = ref<number | null>(null)
const deletingRepo = ref<number | null>(null)
const analyzingAll = ref(false)

// Statistics and charts
const selectedDays = ref(7)
const overviewStats = ref<OverviewStats | null>(null)
const dailyTrends = ref<DailyTrend[]>([])
const trendsChart = ref<HTMLCanvasElement>()

const newRepo = reactive({
  name: '',
  local_path: '',
  description: '',
})

// Computed properties
const netChange = computed(() => {
  if (!overviewStats.value) return 0
  return overviewStats.value.total_added - overviewStats.value.total_deleted
})

const analyzedCount = computed(() => {
  return repositories.value.filter(repo => repo.last_analyzed_at).length
})

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

const handleAddRepository = async () => {
  adding.value = true
  try {
    const response = await api.post('/repositories/', {
      name: newRepo.name,
      local_path: newRepo.local_path,
      description: newRepo.description || undefined,
    })
    
    if (response?.data) {
      repositories.value.push(response.data)
      cancelAdd()
    }
  } catch (err) {
    console.error('Failed to add repository:', err)
  } finally {
    adding.value = false
  }
}

const cancelAdd = () => {
  showAddForm.value = false
  newRepo.name = ''
  newRepo.local_path = ''
  newRepo.description = ''
}

const analyzeRepository = async (repoId: number) => {
  analyzingRepo.value = repoId
  try {
    await api.post(`/repositories/${repoId}/analyze`, {
      days: 30,
      force_refresh: false
    })
    // Refresh repositories to get updated last_analyzed_at
    await fetchRepositories()
    // Refresh overview stats
    await fetchOverviewStats()
  } catch (err) {
    console.error('Failed to analyze repository:', err)
  } finally {
    analyzingRepo.value = null
  }
}

const analyzeAllRepositories = async () => {
  if (repositories.value.length === 0) return
  
  analyzingAll.value = true
  try {
    // Analyze repositories sequentially to avoid overwhelming the system
    for (const repo of repositories.value) {
      analyzingRepo.value = repo.id
      try {
        await api.post(`/repositories/${repo.id}/analyze`, {
          days: 30,
          force_refresh: false
        })
      } catch (err) {
        console.error(`Failed to analyze repository ${repo.name}:`, err)
      }
    }
    // Refresh repositories to get updated last_analyzed_at for all
    await fetchRepositories()
    // Refresh overview stats
    await fetchOverviewStats()
  } catch (err) {
    console.error('Failed to analyze all repositories:', err)
  } finally {
    analyzingAll.value = false
    analyzingRepo.value = null
  }
}

const deleteRepository = async (repoId: number) => {
  if (!confirm('Are you sure you want to delete this repository?')) {
    return
  }
  
  deletingRepo.value = repoId
  try {
    await api.delete(`/repositories/${repoId}`)
    repositories.value = repositories.value.filter(repo => repo.id !== repoId)
    // Refresh overview stats after deletion
    await fetchOverviewStats()
  } catch (err) {
    console.error('Failed to delete repository:', err)
  } finally {
    deletingRepo.value = null
  }
}

const fetchOverviewStats = async () => {
  if (repositories.value.length === 0) {
    overviewStats.value = null
    dailyTrends.value = []
    return
  }
  
  try {
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date(Date.now() - selectedDays.value * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    
    // Fetch cross-repository daily stats
    const dailyResponse = await api.get('/stats/repo-daily', {
      params: {
        date_from: startDate,
        date_to: endDate,
        repo: 'all',
        exclude_ai: false
      }
    })
    
    dailyTrends.value = dailyResponse.data.daily_stats || []
    
    // Calculate overall statistics from daily data
    const stats = {
      total_commits: 0,
      total_added: 0,
      total_deleted: 0,
      total_authors: new Set<number>(),
      repositories_included: dailyResponse.data.repositories_included || []
    }
    
    dailyTrends.value.forEach(day => {
      day.daily_stats.forEach(authorStat => {
        stats.total_commits += authorStat.commits_count
        stats.total_added += authorStat.added_lines
        stats.total_deleted += authorStat.deleted_lines
        stats.total_authors.add(authorStat.author_id)
      })
    })
    
    overviewStats.value = {
      total_commits: stats.total_commits,
      total_added: stats.total_added,
      total_deleted: stats.total_deleted,
      total_authors: stats.total_authors.size,
      repositories_included: stats.repositories_included
    }
    
    // Update chart
    await nextTick()
    setTimeout(() => {
      updateTrendsChart()
    }, 100)
  } catch (err) {
    console.error('Failed to fetch overview statistics:', err)
  }
}

const updateTrendsChart = () => {
  if (!trendsChart.value || dailyTrends.value.length === 0) return
  
  // Check if canvas has proper dimensions
  const rect = trendsChart.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => updateTrendsChart(), 200)
    return
  }
  
  const ctx = trendsChart.value.getContext('2d')
  if (!ctx) return
  
  // Destroy existing chart
  if ((trendsChart.value as any).chart) {
    (trendsChart.value as any).chart.destroy()
  }
  
  const labels = dailyTrends.value.map(trend => 
    new Date(trend.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  )
  
  // Aggregate daily stats
  const dailyCommits = dailyTrends.value.map(trend => 
    trend.daily_stats.reduce((sum, stat) => sum + stat.commits_count, 0)
  )
  const dailyAdded = dailyTrends.value.map(trend => 
    trend.daily_stats.reduce((sum, stat) => sum + stat.added_lines, 0)
  )
  const dailyDeleted = dailyTrends.value.map(trend => 
    trend.daily_stats.reduce((sum, stat) => sum + Math.abs(stat.deleted_lines), 0)
  )
  
  const chart = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Lines Added',
          data: dailyAdded,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: 'rgb(34, 197, 94)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Lines Deleted',
          data: dailyDeleted,
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: 'rgb(239, 68, 68)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Commits',
          data: dailyCommits,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: 'rgb(59, 130, 246)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          yAxisID: 'y1',
          fill: false,
          tension: 0.4,
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
      plugins: {
        title: {
          display: true,
          text: `Repository Activity - Last ${selectedDays.value} Days`,
          font: {
            size: 16,
            weight: 'bold'
          }
        },
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            title: function(context) {
              const dataIndex = context[0].dataIndex
              const trend = dailyTrends.value[dataIndex]
              const authorCount = new Set(trend.daily_stats.map(s => s.author_id)).size
              return `${labels[dataIndex]} - ${authorCount} author${authorCount > 1 ? 's' : ''}`
            },
            label: function(context) {
              const label = context.dataset.label || ''
              const value = context.parsed.y
              return `${label}: ${value.toLocaleString()}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Lines of Code',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            callback: function(value) {
              return typeof value === 'number' ? value.toLocaleString() : value
            }
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Commits',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            callback: function(value) {
              return typeof value === 'number' ? value.toLocaleString() : value
            }
          }
        }
      }
    }
  })
  
  // Store chart reference for cleanup
  ;(trendsChart.value as any).chart = chart
}

onMounted(async () => {
  await fetchRepositories()
  await fetchOverviewStats()
})
</script>