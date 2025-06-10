<template>
  <AppLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Overall Repository Statistics</h1>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedDays"
              @change="fetchOverallStats"
              class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="7">Last 7 days</option>
              <option value="14">Last 14 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
            <label class="flex items-center space-x-2">
              <input
                v-model="excludeAI"
                @change="fetchOverallStats"
                type="checkbox"
                class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              >
              <span class="text-sm text-gray-700">Exclude AI</span>
            </label>
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
          <!-- Enhanced Stats Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Total Commits -->
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
                        {{ overallStats?.total_commits?.toLocaleString() || '0' }}
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
                        +{{ overallStats?.total_added?.toLocaleString() || '0' }}
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

          <!-- Overall Trends Chart -->
          <div v-if="dailyTrends.length > 0" class="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Cross-Repository Activity Trends</h3>
            <div class="h-80">
              <canvas ref="trendsChart"></canvas>
            </div>
          </div>

          <!-- Top Authors Section -->
          <div v-if="topAuthors.length > 0" class="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900">Top Contributors</h3>
              <RouterLink to="/authors" class="text-indigo-600 hover:text-indigo-900 text-sm font-medium">
                View All Authors →
              </RouterLink>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div v-for="(author, index) in topAuthors.slice(0, 6)" :key="author.author_email" class="flex items-center p-4 bg-gray-50 rounded-lg">
                <div class="flex-shrink-0">
                  <div class="h-10 w-10 rounded-full flex items-center justify-center" :class="{
                    'bg-yellow-200 text-yellow-800': index === 0,
                    'bg-gray-200 text-gray-700': index === 1,
                    'bg-orange-200 text-orange-800': index === 2,
                    'bg-blue-200 text-blue-800': index > 2
                  }">
                    <span class="text-sm font-medium">
                      {{ author.author_name.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                </div>
                <div class="ml-4 flex-1">
                  <div class="flex items-center space-x-2">
                    <div class="text-sm font-medium text-gray-900">{{ author.author_name }}</div>
                    <span v-if="author.is_ai_coder" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                      AI
                    </span>
                    <span v-if="index < 3" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" :class="{
                      'bg-yellow-100 text-yellow-800': index === 0,
                      'bg-gray-100 text-gray-800': index === 1,
                      'bg-orange-100 text-orange-800': index === 2
                    }">
                      #{{ index + 1 }}
                    </span>
                  </div>
                  <div class="text-xs text-gray-500">{{ author.commits_count }} commits, {{ (author.added_lines - author.deleted_lines).toLocaleString() }} net lines</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Repositories -->
        <div class="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium text-gray-900">Repository Overview</h2>
            <RouterLink to="/repositories" class="text-indigo-600 hover:text-indigo-900 text-sm font-medium">
              Manage Repositories →
            </RouterLink>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Repository
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Analyzed
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recent Activity
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="repo in repositories" :key="repo.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                          <span class="text-sm font-medium text-white">
                            {{ repo.name.charAt(0).toUpperCase() }}
                          </span>
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ repo.name }}</div>
                        <div class="text-sm text-gray-500 truncate max-w-xs">{{ repo.local_path }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span :class="{
                      'text-green-600': repo.last_analyzed_at && isRecentlyAnalyzed(repo.last_analyzed_at),
                      'text-gray-500': !repo.last_analyzed_at || !isRecentlyAnalyzed(repo.last_analyzed_at)
                    }">
                      {{ repo.last_analyzed_at ? formatDate(repo.last_analyzed_at) : 'Never analyzed' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center space-x-2">
                      <div class="h-2 w-16 bg-gray-200 rounded-full overflow-hidden">
                        <div class="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full" :style="{ width: getActivityLevel(repo) + '%' }"></div>
                      </div>
                      <span class="text-xs text-gray-500">{{ getActivityLevel(repo) }}%</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center space-x-2">
                      <RouterLink
                        :to="`/repositories/${repo.id}/stats`"
                        class="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-md text-sm font-medium transition-colors"
                      >
                        View Stats
                      </RouterLink>
                    </div>
                  </td>
                </tr>
                <tr v-if="repositories.length === 0">
                  <td colspan="4" class="px-6 py-8 text-center text-gray-500">
                    <div class="flex flex-col items-center">
                      <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                      </svg>
                      <p class="text-lg font-medium text-gray-900 mb-2">No repositories yet</p>
                      <p class="text-gray-500 mb-4">Get started by adding your first repository to track code statistics.</p>
                      <RouterLink to="/repositories" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors">
                        Add Repository
                      </RouterLink>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
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
  last_analyzed_at: string | null
}

interface OverallStats {
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

interface AuthorSummary {
  author_email: string
  author_name: string
  is_ai_coder: boolean
  commits_count: number
  added_lines: number
  deleted_lines: number
}

const { api, loading, error } = useApi()
const repositories = ref<Repository[]>([])
const selectedDays = ref(7)
const excludeAI = ref(false)
const overallStats = ref<OverallStats | null>(null)
const dailyTrends = ref<DailyTrend[]>([])
const topAuthors = ref<AuthorSummary[]>([])
const trendsChart = ref<HTMLCanvasElement>()

const netChange = computed(() => {
  if (!overallStats.value) return 0
  return overallStats.value.total_added - overallStats.value.total_deleted
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isRecentlyAnalyzed = (dateString: string) => {
  const analyzedDate = new Date(dateString)
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
  return analyzedDate > oneDayAgo
}

const getActivityLevel = (repo: Repository) => {
  // Simple activity calculation based on recent analysis
  if (!repo.last_analyzed_at) return 0
  const daysSinceAnalysis = Math.floor((Date.now() - new Date(repo.last_analyzed_at).getTime()) / (1000 * 60 * 60 * 24))
  return Math.max(0, Math.min(100, 100 - daysSinceAnalysis * 10))
}

const fetchRepositories = async () => {
  try {
    const response = await api.get('/repositories/')
    repositories.value = response.data
  } catch (err) {
    console.error('Failed to fetch repositories:', err)
  }
}

const fetchOverallStats = async () => {
  if (repositories.value.length === 0) return
  
  try {
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date(Date.now() - selectedDays.value * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    
    // Fetch cross-repository daily stats
    const dailyResponse = await api.get('/stats/repo-daily', {
      params: {
        date_from: startDate,
        date_to: endDate,
        repo: 'all',
        exclude_ai: excludeAI.value
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
    
    const authorStatsMap = new Map<number, {
      commits_count: number
      added_lines: number
      deleted_lines: number
    }>()
    
    dailyTrends.value.forEach(day => {
      day.daily_stats.forEach(authorStat => {
        stats.total_commits += authorStat.commits_count
        stats.total_added += authorStat.added_lines
        stats.total_deleted += authorStat.deleted_lines
        stats.total_authors.add(authorStat.author_id)
        
        if (!authorStatsMap.has(authorStat.author_id)) {
          authorStatsMap.set(authorStat.author_id, {
            commits_count: 0,
            added_lines: 0,
            deleted_lines: 0
          })
        }
        
        const authorData = authorStatsMap.get(authorStat.author_id)!
        authorData.commits_count += authorStat.commits_count
        authorData.added_lines += authorStat.added_lines
        authorData.deleted_lines += authorStat.deleted_lines
      })
    })
    
    overallStats.value = {
      total_commits: stats.total_commits,
      total_added: stats.total_added,
      total_deleted: stats.total_deleted,
      total_authors: stats.total_authors.size,
      repositories_included: stats.repositories_included
    }
    
    // Fetch real author details for all repositories
    const allAuthors = new Map<string, AuthorSummary>()
    
    for (const repo of repositories.value) {
      try {
        const authorResponse = await api.get(`/repositories/${repo.id}/stats/authors`, {
          params: { 
            days: selectedDays.value,
            exclude_ai: excludeAI.value
          }
        })
        
        const repoAuthors = authorResponse.data.authors || authorResponse.data || []
        repoAuthors.forEach((author: any) => {
          const key = author.author_email
          if (!allAuthors.has(key)) {
            allAuthors.set(key, {
              author_email: author.author_email,
              author_name: author.author_name,
              is_ai_coder: author.is_ai_coder || false,
              commits_count: 0,
              added_lines: 0,
              deleted_lines: 0
            })
          }
          
          const existingAuthor = allAuthors.get(key)!
          existingAuthor.commits_count += author.commits_count || 0
          existingAuthor.added_lines += author.added_lines || 0
          existingAuthor.deleted_lines += author.deleted_lines || 0
        })
      } catch (err) {
        console.error(`Failed to fetch authors for repo ${repo.id}:`, err)
      }
    }
    
    // Sort authors by total activity (commits + net lines)
    topAuthors.value = Array.from(allAuthors.values())
      .filter(author => author.commits_count > 0) // Only show authors with activity
      .sort((a, b) => {
        const activityA = a.commits_count + Math.abs(a.added_lines - a.deleted_lines)
        const activityB = b.commits_count + Math.abs(b.added_lines - b.deleted_lines)
        return activityB - activityA
      })
    
    // Update chart
    await nextTick()
    updateTrendsChart()
  } catch (err) {
    console.error('Failed to fetch overall statistics:', err)
  }
}

const updateTrendsChart = () => {
  if (!trendsChart.value || dailyTrends.value.length === 0) return
  
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
          text: `Overall Repository Activity - Last ${selectedDays} Days`,
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
  await fetchOverallStats()
})
</script>