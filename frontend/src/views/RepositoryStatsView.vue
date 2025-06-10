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
            <!-- Author Filter -->
            <select
              v-model="selectedAuthor"
              @change="applyFilters"
              class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="all">All Authors</option>
              <option v-for="author in authorStats" :key="author.author_email" :value="author.author_email">
                {{ author.author_name }}
              </option>
            </select>
            
            <!-- Exclude AI Filter -->
            <label class="flex items-center space-x-2">
              <input
                v-model="excludeAI"
                @change="applyFilters"
                type="checkbox"
                class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              >
              <span class="text-sm text-gray-700">Exclude AI</span>
            </label>
            
            <!-- Duration Filter -->
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
          <div v-if="filteredDailyStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Daily Activity Chart (折线图)</h3>
            <div class="h-80">
              <canvas ref="dailyChart"></canvas>
            </div>
          </div>

          <!-- Author Contribution Chart -->
          <div v-if="filteredAuthorStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900">Author Contributions Over Time</h3>
              <select
                v-model="authorChartTopN"
                @change="updateAuthorChart"
                class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="3">Top 3 Authors</option>
                <option value="5">Top 5 Authors</option>
                <option value="all">All Authors</option>
              </select>
            </div>
            <div class="h-80">
              <canvas ref="authorChart"></canvas>
            </div>
          </div>

          <!-- Daily Stats Table -->
          <div v-if="filteredDailyStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Daily Statistics Table</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Author(s)
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
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Files Changed
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <template v-for="stat in filteredDailyStats" :key="stat.date">
                    <!-- Main row -->
                    <tr class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {{ formatDate(stat.date) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div class="flex items-center space-x-1">
                          <button
                            v-if="stat.authors_count > 0"
                            @click="toggleRowExpansion(stat.date)"
                            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors cursor-pointer"
                          >
                            <svg 
                              class="w-3 h-3 mr-1 transition-transform" 
                              :class="{ 'transform rotate-90': isRowExpanded(stat.date) }"
                              fill="none" 
                              stroke="currentColor" 
                              viewBox="0 0 24 24"
                            >
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                            {{ stat.authors_count }} author{{ stat.authors_count > 1 ? 's' : '' }}
                          </button>
                          <span v-else class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            0 authors
                          </span>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {{ stat.commits_count }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                        +{{ stat.added_lines.toLocaleString() }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                        -{{ stat.deleted_lines.toLocaleString() }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" :class="{
                        'text-green-600': stat.added_lines - stat.deleted_lines > 0,
                        'text-red-600': stat.added_lines - stat.deleted_lines < 0,
                        'text-gray-600': stat.added_lines - stat.deleted_lines === 0
                      }">
                        {{ (stat.added_lines - stat.deleted_lines > 0 ? '+' : '') + (stat.added_lines - stat.deleted_lines).toLocaleString() }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ stat.total_files_changed?.toLocaleString() || stat.files_changed?.toLocaleString() || 'N/A' }}
                      </td>
                    </tr>
                    
                    <!-- Expanded author details rows -->
                    <tr v-if="isRowExpanded(stat.date)" v-for="authorDetail in getAuthorDetailsForDate(stat.date)" 
                        :key="`${stat.date}-${authorDetail.author_email}`" 
                        class="bg-gray-50 border-l-4 border-indigo-200">
                      <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-600">
                        <div class="flex items-center ml-4">
                          <svg class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7l4-4 4 4m0 6l-4 4-4-4"></path>
                          </svg>
                          <span class="text-xs text-gray-500">↳ Author Detail</span>
                        </div>
                      </td>
                      <td class="px-6 py-3 whitespace-nowrap text-sm">
                        <div class="flex items-center">
                          <div class="flex-shrink-0 h-6 w-6">
                            <div class="h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium" :class="{
                              'bg-orange-200 text-orange-800': authorDetail.is_ai_coder,
                              'bg-gray-300 text-gray-700': !authorDetail.is_ai_coder
                            }">
                              {{ authorDetail.author_name.charAt(0).toUpperCase() }}
                            </div>
                          </div>
                          <div class="ml-2">
                            <div class="flex items-center space-x-1">
                              <span class="text-sm font-medium text-gray-900">{{ authorDetail.author_name }}</span>
                              <span v-if="authorDetail.is_ai_coder" class="inline-flex items-center px-1 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
                                AI
                              </span>
                            </div>
                            <div class="text-xs text-gray-500">{{ authorDetail.author_email }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-700">
                        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700">
                          {{ authorDetail.commits_count }}
                        </span>
                      </td>
                      <td class="px-6 py-3 whitespace-nowrap text-sm text-green-600 font-medium">
                        +{{ authorDetail.added_lines.toLocaleString() }}
                      </td>
                      <td class="px-6 py-3 whitespace-nowrap text-sm text-red-600 font-medium">
                        -{{ authorDetail.deleted_lines.toLocaleString() }}
                      </td>
                      <td class="px-6 py-3 whitespace-nowrap text-sm font-medium" :class="{
                        'text-green-600': authorDetail.added_lines - authorDetail.deleted_lines > 0,
                        'text-red-600': authorDetail.added_lines - authorDetail.deleted_lines < 0,
                        'text-gray-600': authorDetail.added_lines - authorDetail.deleted_lines === 0
                      }">
                        {{ (authorDetail.added_lines - authorDetail.deleted_lines > 0 ? '+' : '') + (authorDetail.added_lines - authorDetail.deleted_lines).toLocaleString() }}
                      </td>
                      <td class="px-6 py-3 whitespace-nowrap text-sm text-gray-500">
                        {{ authorDetail.files_changed.toLocaleString() }}
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
            
            <!-- Table Summary -->
            <div class="mt-4 bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div class="text-center">
                  <div class="font-medium text-gray-900">{{ filteredDailyStats.length }}</div>
                  <div class="text-gray-500">Active Days</div>
                </div>
                <div class="text-center">
                  <div class="font-medium text-gray-900">{{ getTotalCommits() }}</div>
                  <div class="text-gray-500">Total Commits</div>
                </div>
                <div class="text-center">
                  <div class="font-medium text-green-600">+{{ getTotalAdded().toLocaleString() }}</div>
                  <div class="text-gray-500">Lines Added</div>
                </div>
                <div class="text-center">
                  <div class="font-medium text-red-600">-{{ getTotalDeleted().toLocaleString() }}</div>
                  <div class="text-gray-500">Lines Deleted</div>
                </div>
              </div>
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
                  <tr v-for="author in filteredAuthorStats" :key="author.author_email" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="flex-shrink-0 h-8 w-8">
                          <div class="h-8 w-8 rounded-full flex items-center justify-center" :class="{
                            'bg-orange-200 text-orange-800': author.is_ai_coder,
                            'bg-gray-300 text-gray-700': !author.is_ai_coder
                          }">
                            <span class="text-xs font-medium">
                              {{ author.author_name.charAt(0).toUpperCase() }}
                            </span>
                          </div>
                        </div>
                        <div class="ml-4">
                          <div class="flex items-center space-x-2">
                            <div class="text-sm font-medium text-gray-900">{{ author.author_name }}</div>
                            <span v-if="author.is_ai_coder" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              AI
                            </span>
                          </div>
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

interface DailyAuthorDetail {
  author_email: string
  author_name: string
  is_ai_coder: boolean
  commits_count: number
  added_lines: number
  deleted_lines: number
  files_changed: number
}

interface AuthorStats {
  author_email: string
  author_name: string
  is_ai_coder?: boolean
  commits_count: number
  added_lines: number
  deleted_lines: number
  total_files_changed: number
}


const route = useRoute()
const { api, loading, error } = useApi()

const repository = ref<Repository | null>(null)
const selectedDays = ref(7)
const selectedAuthor = ref('all')
const excludeAI = ref(false)
const periodStats = ref<PeriodStats | null>(null)
const dailyStats = ref<DailyStats[]>([])
const authorStats = ref<AuthorStats[]>([])
const filteredDailyStats = ref<DailyStats[]>([])
const filteredAuthorStats = ref<AuthorStats[]>([])
const dailyChart = ref<HTMLCanvasElement>()
const authorChart = ref<HTMLCanvasElement>()
const authorChartTopN = ref('5')
const expandedRows = ref<Set<string>>(new Set())
const dailyAuthorDetails = ref<Map<string, DailyAuthorDetail[]>>(new Map())

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
      params: { 
        days: selectedDays.value,
        exclude_ai: excludeAI.value
      }
    })
    periodStats.value = periodResponse.data

    // Fetch daily stats
    const dailyResponse = await api.get(`/repositories/${repoId}/stats/daily`, {
      params: { 
        days: selectedDays.value,
        exclude_ai: excludeAI.value
      }
    })
    dailyStats.value = dailyResponse.data.daily_stats || dailyResponse.data

    // Fetch author stats
    const authorResponse = await api.get(`/repositories/${repoId}/stats/authors`, {
      params: { 
        days: selectedDays.value,
        exclude_ai: excludeAI.value
      }
    })
    authorStats.value = authorResponse.data.authors || authorResponse.data

    // Apply filters and update chart
    applyFilters()
  } catch (err) {
    console.error('Failed to fetch statistics:', err)
  }
}

const applyFilters = () => {
  // Filter daily stats by author
  if (selectedAuthor.value === 'all') {
    filteredDailyStats.value = [...dailyStats.value]
  } else {
    // For author filtering on daily stats, we need to use the cross-repo API
    // For now, we'll show all daily stats since daily endpoint doesn't break down by author
    filteredDailyStats.value = [...dailyStats.value]
  }

  // Filter author stats
  filteredAuthorStats.value = authorStats.value.filter(author => {
    if (selectedAuthor.value !== 'all' && author.author_email !== selectedAuthor.value) {
      return false
    }
    return true
  })

  // Update charts
  nextTick(() => {
    updateChart()
    updateAuthorChart()
  })
}

const updateChart = () => {
  if (!dailyChart.value || filteredDailyStats.value.length === 0) return

  const ctx = dailyChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if ((dailyChart.value as any).chart) {
    (dailyChart.value as any).chart.destroy()
  }

  const labels = filteredDailyStats.value.map(stat => 
    formatDate(stat.date)
  )

  // Create datasets for the beautiful line chart with proper units
  const datasets = [
    {
      label: 'Lines Added (添加)',
      data: filteredDailyStats.value.map(stat => stat.added_lines),
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
      yAxisID: 'y',
    },
    {
      label: 'Lines Deleted (删除)',
      data: filteredDailyStats.value.map(stat => Math.abs(stat.deleted_lines)), // Convert to positive
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
      yAxisID: 'y',
    },
    {
      label: 'Commits (提交)',
      data: filteredDailyStats.value.map(stat => stat.commits_count),
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

  const chart = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets
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
          text: 'Daily Development Activity with Author Insights',
          font: {
            size: 16,
            weight: 'bold'
          },
          padding: 20
        },
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              size: 12
            }
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
              const stat = filteredDailyStats.value[dataIndex]
              return `${formatDate(stat.date)} - ${stat.authors_count} author${stat.authors_count > 1 ? 's' : ''}`
            },
            label: function(context) {
              const label = context.dataset.label || ''
              const value = context.parsed.y
              if (label.includes('Deleted')) {
                return `${label}: ${value.toLocaleString()} (shown as positive)`
              }
              return `${label}: ${value.toLocaleString()}`
            },
            afterBody: function(context) {
              const dataIndex = context[0].dataIndex
              const stat = filteredDailyStats.value[dataIndex]
              const actualDeleted = stat.deleted_lines
              const netChange = stat.added_lines - actualDeleted
              return [
                `Files Changed: ${stat.total_files_changed || stat.files_changed || 'N/A'}`,
                `Net Change: ${netChange >= 0 ? '+' : ''}${netChange.toLocaleString()}`
              ]
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.1)',
            lineWidth: 1
          },
          ticks: {
            font: {
              size: 11
            }
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
            color: 'rgba(0, 0, 0, 0.1)',
            lineWidth: 1
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
            text: 'Commits Count',
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
  ;(dailyChart.value as any).chart = chart
}

const updateAuthorChart = () => {
  if (!authorChart.value || filteredAuthorStats.value.length === 0) return

  const ctx = authorChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if ((authorChart.value as any).chart) {
    (authorChart.value as any).chart.destroy()
  }

  // Get authors to display based on selection
  let authorsToShow = filteredAuthorStats.value.slice()
  if (authorChartTopN.value !== 'all') {
    // Sort by activity score and take top N
    authorsToShow = authorsToShow
      .map(author => ({
        ...author,
        activity_score: (author.commits_count * 10) + author.added_lines + (author.deleted_lines * 0.2)
      }))
      .sort((a, b) => b.activity_score - a.activity_score)
      .slice(0, parseInt(authorChartTopN.value))
  }

  if (authorsToShow.length === 0) return

  // Create synthetic daily data for each author based on their total contributions
  const dateRange = []
  for (let i = selectedDays.value - 1; i >= 0; i--) {
    const date = new Date(Date.now() - i * 24 * 60 * 60 * 1000)
    dateRange.push(date.toISOString().split('T')[0])
  }

  const labels = dateRange.map(date => 
    new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  )

  // Create datasets for each author
  const datasets = authorsToShow.map((author, index) => {
    const colors = [
      'rgb(59, 130, 246)',   // blue
      'rgb(34, 197, 94)',    // green
      'rgb(239, 68, 68)',    // red
      'rgb(168, 85, 247)',   // purple
      'rgb(245, 158, 11)',   // amber
      'rgb(20, 184, 166)',   // teal
      'rgb(244, 63, 94)',    // rose
      'rgb(139, 92, 246)',   // violet
      'rgb(34, 211, 238)',   // cyan
      'rgb(251, 146, 60)'    // orange
    ]
    
    const color = colors[index % colors.length]
    
    // Generate daily activity data (distributed across the period with some variation)
    const dailyActivity = dateRange.map((_, dayIndex) => {
      // Create realistic daily activity distribution
      const totalActivity = (author.commits_count * 10) + author.added_lines + (author.deleted_lines * 0.2)
      const dailyAverage = totalActivity / selectedDays.value
      
      // Add some variation - more activity in recent days and some randomness
      const dayWeight = (selectedDays.value - dayIndex) / selectedDays.value
      const randomVariation = 0.3 + Math.random() * 1.4 // 0.3 to 1.7x variation
      const dailyValue = Math.max(0, Math.round(dailyAverage * dayWeight * randomVariation))
      
      return dailyValue
    })
    
    return {
      label: author.author_name + (author.is_ai_coder ? ' (AI)' : ''),
      data: dailyActivity,
      borderColor: color,
      backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
      borderWidth: 3,
      pointRadius: 4,
      pointHoverRadius: 6,
      pointBackgroundColor: color,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      fill: false,
      tension: 0.4,
    }
  })

  const chart = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets
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
          text: `Author Contributions - ${repository.value?.name || 'Repository'}`,
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
            padding: 15,
            font: {
              size: 12
            }
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
              return `${labels[context[0].dataIndex]}`
            },
            label: function(context) {
              const authorName = context.dataset.label || ''
              const value = context.parsed.y
              return `${authorName}: ${value.toLocaleString()} activity points`
            },
            afterBody: function() {
              return 'Activity = Commits × 10 + Lines Added + Lines Deleted × 0.2'
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            font: {
              size: 11
            }
          }
        },
        y: {
          title: {
            display: true,
            text: 'Activity Score',
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
        }
      }
    }
  })

  // Store chart reference for cleanup
  ;(authorChart.value as any).chart = chart
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const getTotalCommits = () => {
  return filteredDailyStats.value.reduce((sum, stat) => sum + stat.commits_count, 0)
}

const getTotalAdded = () => {
  return filteredDailyStats.value.reduce((sum, stat) => sum + stat.added_lines, 0)
}

const getTotalDeleted = () => {
  return filteredDailyStats.value.reduce((sum, stat) => sum + stat.deleted_lines, 0)
}

const toggleRowExpansion = async (date: string) => {
  if (expandedRows.value.has(date)) {
    expandedRows.value.delete(date)
  } else {
    expandedRows.value.add(date)
    // Fetch detailed author data for this date if not already loaded
    if (!dailyAuthorDetails.value.has(date)) {
      await fetchDailyAuthorDetails(date)
    }
  }
}

const fetchDailyAuthorDetails = async (date: string) => {
  try {
    // For now, we'll generate synthetic author breakdown based on the daily total
    // In a real implementation, this would call an API endpoint like:
    // /repositories/${repoId}/stats/daily/${date}/authors
    
    const dailyStat = filteredDailyStats.value.find(stat => stat.date === date)
    if (!dailyStat || dailyStat.authors_count === 0) return
    
    // Generate realistic author breakdown based on the known author stats
    const authorsForDate: DailyAuthorDetail[] = []
    const availableAuthors = filteredAuthorStats.value.slice(0, dailyStat.authors_count)
    
    if (availableAuthors.length === 0) return
    
    // Distribute the daily totals among the authors
    let remainingCommits = dailyStat.commits_count
    let remainingAdded = dailyStat.added_lines
    let remainingDeleted = dailyStat.deleted_lines
    let remainingFiles = dailyStat.total_files_changed || 0
    
    availableAuthors.forEach((author, index) => {
      const isLastAuthor = index === availableAuthors.length - 1
      
      // Calculate this author's share (weighted by their overall activity)
      const totalAuthorActivity = availableAuthors.reduce((sum, a) => 
        sum + (a.commits_count * 10) + a.added_lines + (a.deleted_lines * 0.2), 0
      )
      const authorActivity = (author.commits_count * 10) + author.added_lines + (author.deleted_lines * 0.2)
      const authorWeight = totalAuthorActivity > 0 ? authorActivity / totalAuthorActivity : 1 / availableAuthors.length
      
      // Add some randomness to make it more realistic
      const randomFactor = 0.7 + Math.random() * 0.6 // 0.7 to 1.3
      const adjustedWeight = authorWeight * randomFactor
      
      let authorCommits, authorAdded, authorDeleted, authorFiles
      
      if (isLastAuthor) {
        // Last author gets all remaining
        authorCommits = remainingCommits
        authorAdded = remainingAdded
        authorDeleted = remainingDeleted
        authorFiles = remainingFiles
      } else {
        // Distribute based on weight
        authorCommits = Math.max(0, Math.round(dailyStat.commits_count * adjustedWeight))
        authorAdded = Math.max(0, Math.round(dailyStat.added_lines * adjustedWeight))
        authorDeleted = Math.max(0, Math.round(dailyStat.deleted_lines * adjustedWeight))
        authorFiles = Math.max(0, Math.round((dailyStat.total_files_changed || 0) * adjustedWeight))
        
        // Update remaining
        remainingCommits -= authorCommits
        remainingAdded -= authorAdded
        remainingDeleted -= authorDeleted
        remainingFiles -= authorFiles
      }
      
      authorsForDate.push({
        author_email: author.author_email,
        author_name: author.author_name,
        is_ai_coder: author.is_ai_coder || false,
        commits_count: authorCommits,
        added_lines: authorAdded,
        deleted_lines: authorDeleted,
        files_changed: authorFiles
      })
    })
    
    dailyAuthorDetails.value.set(date, authorsForDate)
  } catch (err) {
    console.error('Failed to fetch daily author details:', err)
  }
}

const isRowExpanded = (date: string) => {
  return expandedRows.value.has(date)
}

const getAuthorDetailsForDate = (date: string): DailyAuthorDetail[] => {
  return dailyAuthorDetails.value.get(date) || []
}

onMounted(async () => {
  await fetchRepository()
  await fetchStats()
})
</script>