<template>
  <AppLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <!-- Header -->
        <div class="flex justify-between items-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Authors & Contributions</h1>
          <div class="flex items-center space-x-4">
            <!-- Date Range Filter -->
            <select
              v-model="selectedDays"
              @change="fetchAuthorsData"
              class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="7">Last 7 days</option>
              <option value="14">Last 14 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
            
            <!-- Chart Top N Filter -->
            <select
              v-model="chartTopN"
              @change="updateChart"
              class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="3">Top 3 Authors</option>
              <option value="5">Top 5 Authors</option>
              <option value="10">Top 10 Authors</option>
            </select>
            
            <!-- Exclude AI Filter -->
            <label class="flex items-center space-x-2">
              <input
                v-model="excludeAI"
                @change="fetchAuthorsData"
                type="checkbox"
                class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              >
              <span class="text-sm text-gray-700">Exclude AI</span>
            </label>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8">
          <div class="text-gray-500">Loading authors data...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {{ error }}
        </div>

        <!-- Content -->
        <div v-else class="space-y-8">
          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Total Authors -->
            <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
              <div class="p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-6 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        Total Authors
                      </dt>
                      <dd class="text-2xl font-bold text-gray-900">
                        {{ allAuthors.length }}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Active Authors -->
            <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
              <div class="p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-6 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        Active Authors
                      </dt>
                      <dd class="text-2xl font-bold text-gray-900">
                        {{ activeAuthors.length }}
                      </dd>
                      <dd class="text-xs text-gray-400">Last {{ selectedDays }} days</dd>
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
                        {{ totalCommits.toLocaleString() }}
                      </dd>
                      <dd class="text-xs text-gray-400">Last {{ selectedDays }} days</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Total Lines Changed -->
            <div class="bg-white overflow-hidden shadow-lg rounded-lg border border-gray-200">
              <div class="p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="{
                      'bg-green-500': totalNetChange >= 0,
                      'bg-red-500': totalNetChange < 0
                    }">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM6 6v14h12V6H6zm3-2V3h6v1H9z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-6 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        Net Lines
                      </dt>
                      <dd class="text-2xl font-bold" :class="{
                        'text-green-600': totalNetChange >= 0,
                        'text-red-600': totalNetChange < 0
                      }">
                        {{ (totalNetChange >= 0 ? '+' : '') + totalNetChange.toLocaleString() }}
                      </dd>
                      <dd class="text-xs text-gray-400">Last {{ selectedDays }} days</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Authors Commits Chart -->
          <div v-if="dailyAuthorsData.length > 0" class="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900">Authors Commits Over Time</h3>
              <select
                v-model="chartTopN"
                @change="updateChart"
                class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="3">Top 3 Authors</option>
                <option value="5">Top 5 Authors</option>
                <option value="10">Top 10 Authors</option>
              </select>
            </div>
            <div class="h-80">
              <canvas ref="authorsChart"></canvas>
            </div>
          </div>

          <!-- Authors Code Added Chart -->
          <div v-if="dailyAuthorsData.length > 0" class="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900">Authors Code Added Over Time</h3>
              <select
                v-model="codeAddedChartTopN"
                @change="updateCodeAddedChart"
                class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="3">Top 3 Authors</option>
                <option value="5">Top 5 Authors</option>
                <option value="10">Top 10 Authors</option>
              </select>
            </div>
            <div class="h-80">
              <canvas ref="codeAddedChart"></canvas>
            </div>
          </div>

          <!-- Authors Table -->
          <div v-if="allAuthors.length > 0" class="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h3 class="text-lg font-medium text-gray-900 mb-4">All Authors Contributions</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th @click="sortBy('author_name')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                      <div class="flex items-center space-x-1">
                        <span>Author</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                        </svg>
                      </div>
                    </th>
                    <th @click="sortBy('commits_count')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                      <div class="flex items-center space-x-1">
                        <span>Commits</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                        </svg>
                      </div>
                    </th>
                    <th @click="sortBy('added_lines')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                      <div class="flex items-center space-x-1">
                        <span>Lines Added</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                        </svg>
                      </div>
                    </th>
                    <th @click="sortBy('deleted_lines')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                      <div class="flex items-center space-x-1">
                        <span>Lines Deleted</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                        </svg>
                      </div>
                    </th>
                    <th @click="sortBy('net_change')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                      <div class="flex items-center space-x-1">
                        <span>Net Change</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                        </svg>
                      </div>
                    </th>
                    <th @click="sortBy('ai_lines_percentage')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                      <div class="flex items-center space-x-1">
                        <span>AI Assistance</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"></path>
                        </svg>
                      </div>
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Active Repositories
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="author in sortedAuthors" :key="author.author_email" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                          <div class="h-10 w-10 rounded-full flex items-center justify-center" :class="{
                            'bg-orange-200 text-orange-800': author.is_ai_coder,
                            'bg-gray-300 text-gray-700': !author.is_ai_coder
                          }">
                            <span class="text-sm font-medium">
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
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {{ author.commits_count }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                      +{{ author.added_lines.toLocaleString() }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                      -{{ author.deleted_lines.toLocaleString() }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" :class="{
                      'text-green-600': author.net_change > 0,
                      'text-red-600': author.net_change < 0,
                      'text-gray-600': author.net_change === 0
                    }">
                      {{ (author.net_change > 0 ? '+' : '') + author.net_change.toLocaleString() }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center space-x-2">
                        <div class="flex-shrink-0 w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            class="h-2 rounded-full transition-all duration-300"
                            :class="{
                              'bg-orange-500': getAuthorAiPercentage(author.author_email) > 0,
                              'bg-gray-300': getAuthorAiPercentage(author.author_email) === 0
                            }"
                            :style="{ width: Math.min(100, getAuthorAiPercentage(author.author_email)) + '%' }"
                          ></div>
                        </div>
                        <span class="text-sm font-medium" :class="{
                          'text-orange-600': getAuthorAiPercentage(author.author_email) > 0,
                          'text-gray-500': getAuthorAiPercentage(author.author_email) === 0
                        }">
                          {{ getAuthorAiPercentage(author.author_email).toFixed(1) }}%
                        </span>
                        <svg v-if="author.is_ai_coder" class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex flex-wrap gap-1">
                        <RouterLink
                          v-for="repo in author.repositories"
                          :key="repo.id"
                          :to="`/repositories/${repo.id}/stats`"
                          class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-indigo-100 text-indigo-800 hover:bg-indigo-200 transition-colors"
                        >
                          {{ repo.name }}
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
}

interface AuthorSummary {
  author_email: string
  author_name: string
  is_ai_coder: boolean
  commits_count: number
  added_lines: number
  deleted_lines: number
  net_change: number
  repositories: Repository[]
  activity_score: number
}

interface DailyAuthorData {
  date: string
  author_email: string
  author_name: string
  commits_count: number
  added_lines: number
  deleted_lines: number
  files_changed: number
}

const { api, loading, error, getOverallAiStats, getOverallAiTrends } = useApi()
const selectedDays = ref(30)
const chartTopN = ref(5)
const excludeAI = ref(false)
const sortField = ref('activity_score')
const sortDirection = ref<'asc' | 'desc'>('desc')

const repositories = ref<Repository[]>([])
const allAuthors = ref<AuthorSummary[]>([])
const dailyAuthorsData = ref<DailyAuthorData[]>([])
const authorsChart = ref<HTMLCanvasElement>()
const codeAddedChart = ref<HTMLCanvasElement>()
const codeAddedChartTopN = ref(5)

// AI Statistics
const allAuthorAiStats = ref<Map<string, number>>(new Map())

const activeAuthors = computed(() => 
  allAuthors.value.filter(author => author.commits_count > 0)
)

const totalCommits = computed(() => 
  allAuthors.value.reduce((sum, author) => sum + author.commits_count, 0)
)

const totalNetChange = computed(() => 
  allAuthors.value.reduce((sum, author) => sum + author.net_change, 0)
)

const sortedAuthors = computed(() => {
  return [...allAuthors.value].sort((a, b) => {
    const aValue = a[sortField.value as keyof AuthorSummary] as number
    const bValue = b[sortField.value as keyof AuthorSummary] as number
    
    if (sortDirection.value === 'desc') {
      return bValue - aValue
    } else {
      return aValue - bValue
    }
  })
})

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortField.value = field
    sortDirection.value = 'desc'
  }
}

const getAuthorAiPercentage = (authorEmail: string): number => {
  return allAuthorAiStats.value.get(authorEmail) || 0
}

const fetchRepositories = async () => {
  try {
    const response = await api.get('/repositories/')
    repositories.value = response.data
  } catch (err) {
    console.error('Failed to fetch repositories:', err)
  }
}

const fetchAuthorsData = async () => {
  if (repositories.value.length === 0) return
  
  try {
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date(Date.now() - selectedDays.value * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    
    // Fetch detailed author data from each repository
    const authorsMap = new Map<string, AuthorSummary>()
    const dailyDataMap = new Map<string, DailyAuthorData[]>() // Map by author email
    
    for (const repo of repositories.value) {
      try {
        // Fetch author summary stats
        const authorResponse = await api.get(`/repositories/${repo.id}/stats/authors`, {
          params: { 
            days: selectedDays.value,
            exclude_ai: excludeAI.value
          }
        })
        
        const repoAuthors = authorResponse.data.authors || authorResponse.data || []
        repoAuthors.forEach((author: any) => {
          const key = author.author_email
          if (!authorsMap.has(key)) {
            authorsMap.set(key, {
              author_email: author.author_email,
              author_name: author.author_name,
              is_ai_coder: author.is_ai_coder || false,
              commits_count: 0,
              added_lines: 0,
              deleted_lines: 0,
              net_change: 0,
              repositories: [],
              activity_score: 0
            })
          }
          
          const existingAuthor = authorsMap.get(key)!
          existingAuthor.commits_count += author.commits_count || 0
          existingAuthor.added_lines += author.added_lines || 0
          existingAuthor.deleted_lines += author.deleted_lines || 0
          existingAuthor.net_change = existingAuthor.added_lines - existingAuthor.deleted_lines
          
          // Add repository if author has activity in it
          if (author.commits_count > 0) {
            existingAuthor.repositories.push({
              id: repo.id,
              name: repo.name,
              local_path: repo.local_path
            })
          }
          
          // Calculate activity score: commits_count * 10 + added_lines + deleted_lines * 0.2
          existingAuthor.activity_score = (existingAuthor.commits_count * 10) + existingAuthor.added_lines + (existingAuthor.deleted_lines * 0.2)
        })
        
        // Fetch real daily author data from the API
        try {
          const dailyAuthorResponse = await api.get(`/repositories/${repo.id}/stats/daily-authors`, {
            params: { 
              days: selectedDays.value,
              exclude_ai: excludeAI.value
            }
          })
          
          const repoDailyData = dailyAuthorResponse.data.daily_stats || []
          repoDailyData.forEach((dayData: any) => {
            const date = dayData.date
            const dayAuthors = dayData.authors || []
            
            dayAuthors.forEach((authorData: any) => {
              const authorEmail = authorData.author.email
              if (!dailyDataMap.has(authorEmail)) {
                dailyDataMap.set(authorEmail, [])
              }
              
              // Add real daily data
              dailyDataMap.get(authorEmail)!.push({
                date: date,
                author_email: authorData.author.email,
                author_name: authorData.author.name,
                commits_count: authorData.commits_count || 0,
                added_lines: authorData.added_lines || 0,
                deleted_lines: authorData.deleted_lines || 0,
                files_changed: authorData.files_changed || 0
              })
            })
          })
        } catch (err) {
          console.error(`Failed to fetch daily author data for repo ${repo.id}:`, err)
        }
      } catch (err) {
        console.error(`Failed to fetch authors for repo ${repo.id}:`, err)
      }
    }
    
    allAuthors.value = Array.from(authorsMap.values())
      .filter(author => author.commits_count > 0) // Only show authors with activity
    
    // Convert daily data map to array format
    const allDailyData: DailyAuthorData[] = []
    dailyDataMap.forEach((authorDays, authorEmail) => {
      allDailyData.push(...authorDays)
    })
    dailyAuthorsData.value = allDailyData
    
    // Fetch AI statistics for all authors
    await fetchAuthorAiStats()
    
    // Update charts
    await nextTick()
    updateChart()
    updateCodeAddedChart()
  } catch (err) {
    console.error('Failed to fetch authors data:', err)
  }
}

const fetchAuthorAiStats = async () => {
  if (repositories.value.length === 0) return
  
  try {
    // Clear existing AI stats
    allAuthorAiStats.value.clear()
    
    // Fetch AI author stats for each repository
    for (const repo of repositories.value) {
      try {
        const aiAuthorResponse = await api.get(`/repositories/${repo.id}/stats/ai-authors`, {
          params: { days: selectedDays.value }
        })
        
        const aiAuthors = aiAuthorResponse.data || []
        aiAuthors.forEach((aiAuthor: any) => {
          const email = aiAuthor.author_email
          const currentPercentage = allAuthorAiStats.value.get(email) || 0
          const newPercentage = aiAuthor.ai_lines_percentage || 0
          
          // Take the average AI percentage across repositories for this author
          const existingRepoCount = Array.from(allAuthorAiStats.value.keys()).filter(e => e === email).length
          const avgPercentage = (currentPercentage * existingRepoCount + newPercentage) / (existingRepoCount + 1)
          
          allAuthorAiStats.value.set(email, avgPercentage)
        })
      } catch (err) {
        console.error(`Failed to fetch AI stats for repo ${repo.id}:`, err)
      }
    }
  } catch (err) {
    console.error('Failed to fetch AI author stats:', err)
  }
}

const updateChart = () => {
  if (!authorsChart.value || dailyAuthorsData.value.length === 0) return
  
  const ctx = authorsChart.value.getContext('2d')
  if (!ctx) return
  
  // Destroy existing chart
  if ((authorsChart.value as any).chart) {
    (authorsChart.value as any).chart.destroy()
  }
  
  // Get top N authors by commits count
  const topAuthors = [...allAuthors.value]
    .sort((a, b) => b.commits_count - a.commits_count)
    .slice(0, chartTopN.value)
  
  if (topAuthors.length === 0) return
  
  // Get unique dates and sort them
  const uniqueDates = [...new Set(dailyAuthorsData.value.map(data => data.date))]
    .sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
  
  const labels = uniqueDates.map(date => 
    new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  )
  
  // Create datasets for each top author
  const datasets = topAuthors.map((author, index) => {
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
    
    // Get daily activity for this author
    const dailyActivity = uniqueDates.map(date => {
      const authorData = dailyAuthorsData.value.filter(data => 
        data.date === date && data.author_email === author.author_email
      )
      return authorData.reduce((sum, data) => sum + data.commits_count, 0)
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
          text: `Top ${chartTopN.value} Authors Commits Over Time`,
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
            padding: 15
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
              return `${authorName}: ${value.toLocaleString()} commits`
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
          title: {
            display: true,
            text: 'Commits Count',
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
  ;(authorsChart.value as any).chart = chart
}

const updateCodeAddedChart = () => {
  if (!codeAddedChart.value || dailyAuthorsData.value.length === 0) return
  
  const ctx = codeAddedChart.value.getContext('2d')
  if (!ctx) return
  
  // Destroy existing chart
  if ((codeAddedChart.value as any).chart) {
    (codeAddedChart.value as any).chart.destroy()
  }
  
  // Get top N authors by added lines
  const topAuthors = [...allAuthors.value]
    .sort((a, b) => b.added_lines - a.added_lines)
    .slice(0, codeAddedChartTopN.value)
  
  if (topAuthors.length === 0) return
  
  // Get unique dates and sort them
  const uniqueDates = [...new Set(dailyAuthorsData.value.map(data => data.date))]
    .sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
  
  const labels = uniqueDates.map(date => 
    new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  )
  
  // Create datasets for each top author
  const datasets = topAuthors.map((author, index) => {
    const colors = [
      'rgb(34, 197, 94)',    // green
      'rgb(59, 130, 246)',   // blue  
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
    
    // Get daily added lines for this author
    const dailyActivity = uniqueDates.map(date => {
      const authorData = dailyAuthorsData.value.filter(data => 
        data.date === date && data.author_email === author.author_email
      )
      return authorData.reduce((sum, data) => sum + data.added_lines, 0)
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
          text: `Top ${codeAddedChartTopN.value} Authors Code Added Over Time`,
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
            padding: 15
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
              return `${authorName}: ${value.toLocaleString()} lines added`
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
          title: {
            display: true,
            text: 'Lines Added',
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
  ;(codeAddedChart.value as any).chart = chart
}

onMounted(async () => {
  await fetchRepositories()
  await fetchAuthorsData()
})
</script>