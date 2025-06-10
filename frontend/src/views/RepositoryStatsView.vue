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

          <!-- AI Statistics Section -->
          <div v-if="aiStats" class="bg-gradient-to-r from-orange-50 to-purple-50 p-6 rounded-lg border border-orange-200">
            <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <svg class="w-5 h-5 text-orange-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              AI-Powered Coding Analytics
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- AI Assistance Percentage -->
              <div class="bg-white p-4 rounded-lg shadow-sm border border-orange-100">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500">AI-Assisted Code</div>
                    <div class="text-2xl font-bold text-orange-600">{{ aiStats.ai_lines_percentage }}%</div>
                    <div class="text-xs text-gray-400">{{ aiStats.ai_assisted_lines?.toLocaleString() ?? '0' }} of {{ aiStats.total_lines?.toLocaleString() ?? '0' }} lines</div>
                  </div>
                </div>
              </div>

              <!-- AI Commits -->
              <div class="bg-white p-4 rounded-lg shadow-sm border border-purple-100">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500">AI-Assisted Commits</div>
                    <div class="text-2xl font-bold text-purple-600">{{ aiStats.ai_assisted_commits?.toLocaleString() ?? '0' }}</div>
                    <div class="text-xs text-gray-400">{{ aiStats.ai_commits_percentage }}% of all commits</div>
                  </div>
                </div>
              </div>

              <!-- AI Authors -->
              <div class="bg-white p-4 rounded-lg shadow-sm border border-indigo-100">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-indigo-500 rounded-lg flex items-center justify-center">
                      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-500">AI Contributors</div>
                    <div class="text-2xl font-bold text-indigo-600">{{ authorStats.filter(a => a.is_ai_coder).length }}</div>
                    <div class="text-xs text-gray-400">AI co-authors detected</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Trends Chart -->
          <div v-if="aiTrends.length > 0" class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 mb-4">AI Assistance Trends</h3>
            <div class="h-80">
              <canvas ref="aiTrendsChart"></canvas>
            </div>
          </div>

          <!-- Daily Activity Chart -->
          <div v-if="filteredDailyStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Daily Activity Chart (折线图)</h3>
            <div class="h-80">
              <canvas ref="dailyChart"></canvas>
            </div>
          </div>

          <!-- Author Commits Over Time Chart -->
          <div v-if="filteredAuthorStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900">Author Commits Over Time</h3>
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

          <!-- Author Code Added Over Time Chart -->
          <div v-if="filteredAuthorStats.length > 0" class="bg-white p-6 rounded-lg shadow">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium text-gray-900">Author Code Added Over Time</h3>
              <select
                v-model="codeAddedChartTopN"
                @change="updateCodeAddedChart"
                class="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="3">Top 3 Authors</option>
                <option value="5">Top 5 Authors</option>
                <option value="all">All Authors</option>
              </select>
            </div>
            <div class="h-80">
              <canvas ref="codeAddedChart"></canvas>
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
                        {{ stat.total_files_changed?.toLocaleString() || 'N/A' }}
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
const { api, loading, error, getAiCodingStats, getAiAuthorStats, getAiTrends } = useApi()

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
const codeAddedChart = ref<HTMLCanvasElement>()

// AI Statistics
const aiStats = ref<any>(null)
const aiTrends = ref<any[]>([])
const aiAuthorStats = ref<any[]>([])
const aiTrendsChart = ref<HTMLCanvasElement>()
const authorChartTopN = ref('5')
const codeAddedChartTopN = ref('5')
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
    
    // Fetch AI statistics
    await fetchAiStats()
  } catch (err) {
    console.error('Failed to fetch statistics:', err)
  }
}

const fetchAiStats = async () => {
  try {
    // Fetch AI coding stats
    const aiStatsResponse = await getAiCodingStats(repoId, selectedDays.value)
    if (aiStatsResponse?.data) {
      aiStats.value = aiStatsResponse.data
    }

    // Fetch AI author stats
    const aiAuthorResponse = await getAiAuthorStats(repoId, selectedDays.value)
    if (aiAuthorResponse?.data) {
      aiAuthorStats.value = aiAuthorResponse.data
    }

    // Fetch AI trends
    const aiTrendsResponse = await getAiTrends(repoId, selectedDays.value)
    if (aiTrendsResponse?.data) {
      aiTrends.value = aiTrendsResponse.data
      await nextTick()
      updateAiTrendsChart()
    }
  } catch (err) {
    console.error('Failed to fetch AI statistics:', err)
  }
}

const updateAiTrendsChart = () => {
  if (!aiTrendsChart.value || aiTrends.value.length === 0) return
  
  // Check if canvas has proper dimensions
  const rect = aiTrendsChart.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => updateAiTrendsChart(), 200)
    return
  }
  
  const ctx = aiTrendsChart.value.getContext('2d')
  if (!ctx) return
  
  // Destroy existing chart
  if ((aiTrendsChart.value as any).chart) {
    (aiTrendsChart.value as any).chart.destroy()
  }
  
  const labels = aiTrends.value.map(trend => 
    new Date(trend.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    })
  )
  
  const aiPercentages = aiTrends.value.map(trend => trend.ai_lines_percentage)
  const aiLines = aiTrends.value.map(trend => trend.ai_assisted_lines)
  
  const chart = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'AI Assistance %',
          data: aiPercentages,
          borderColor: 'rgb(249, 115, 22)',
          backgroundColor: 'rgba(249, 115, 22, 0.1)',
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: 'rgb(249, 115, 22)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: true,
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'AI-Assisted Lines',
          data: aiLines,
          borderColor: 'rgb(168, 85, 247)',
          backgroundColor: 'rgba(168, 85, 247, 0.1)',
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: 'rgb(168, 85, 247)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          fill: false,
          tension: 0.4,
          yAxisID: 'y1'
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
          text: `AI Assistance Trends - ${repository.value?.name} (${selectedDays.value} days)`,
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
            label: function(context) {
              const label = context.dataset.label || ''
              const value = context.parsed.y
              if (label.includes('%')) {
                return `${label}: ${value.toFixed(1)}%`
              }
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
            text: 'AI Assistance %',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          min: 0,
          max: 100,
          ticks: {
            callback: function(value) {
              return typeof value === 'number' ? value.toFixed(0) + '%' : value
            }
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Lines of Code',
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
  ;(aiTrendsChart.value as any).chart = chart
}

const applyFilters = async () => {
  // Clear cached daily author details when filters change
  dailyAuthorDetails.value.clear()
  expandedRows.value.clear()
  
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
  await nextTick()
  // Add delays to ensure containers are properly rendered
  setTimeout(() => updateChart(), 100)
  setTimeout(() => updateAuthorChart(), 150)
  setTimeout(() => updateCodeAddedChart(), 200)
}

const updateChart = () => {
  if (!dailyChart.value || filteredDailyStats.value.length === 0) return

  // Check if canvas has proper dimensions
  const rect = dailyChart.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => updateChart(), 200)
    return
  }

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
                `Files Changed: ${stat.total_files_changed || 'N/A'}`,
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

const updateAuthorChart = async () => {
  if (!authorChart.value || filteredAuthorStats.value.length === 0) return

  // Check if canvas has proper dimensions
  const rect = authorChart.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => updateAuthorChart(), 200)
    return
  }

  const ctx = authorChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if ((authorChart.value as any).chart) {
    (authorChart.value as any).chart.destroy()
  }

  // Get authors to display based on selection
  let authorsToShow = filteredAuthorStats.value.slice()
  if (authorChartTopN.value !== 'all') {
    // Sort by commits count and take top N
    authorsToShow = authorsToShow
      .sort((a, b) => b.commits_count - a.commits_count)
      .slice(0, parseInt(authorChartTopN.value))
  }

  if (authorsToShow.length === 0) return

  // Fetch real daily author data
  let dailyAuthorData: any[] = []
  try {
    const response = await api.get(`/repositories/${repoId}/stats/daily-authors`, {
      params: { 
        days: selectedDays.value,
        exclude_ai: excludeAI.value
      }
    })
    dailyAuthorData = response.data.daily_stats || []
  } catch (error) {
    console.error('Failed to fetch daily author data for chart:', error)
    return
  }

  // Create date range for labels
  const dateRange: string[] = []
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

  // Create datasets for each author using real daily data
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
    
    // Get real daily commits data for this author
    const dailyActivity = dateRange.map(date => {
      const dayData = dailyAuthorData.find(d => d.date === date)
      if (!dayData || !dayData.authors) return 0
      
      const authorData = dayData.authors.find((a: any) => a.author.email === author.author_email)
      return authorData ? authorData.commits_count : 0
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
          text: `Author Commits Over Time - ${repository.value?.name || 'Repository'}`,
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
              return `${authorName}: ${value.toLocaleString()} commits`
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
  ;(authorChart.value as any).chart = chart
}

const updateCodeAddedChart = async () => {
  if (!codeAddedChart.value || filteredAuthorStats.value.length === 0) return

  // Check if canvas has proper dimensions
  const rect = codeAddedChart.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => updateCodeAddedChart(), 200)
    return
  }

  const ctx = codeAddedChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if ((codeAddedChart.value as any).chart) {
    (codeAddedChart.value as any).chart.destroy()
  }

  // Get authors to display based on selection
  let authorsToShow = filteredAuthorStats.value.slice()
  if (codeAddedChartTopN.value !== 'all') {
    // Sort by added lines and take top N
    authorsToShow = authorsToShow
      .sort((a, b) => b.added_lines - a.added_lines)
      .slice(0, parseInt(codeAddedChartTopN.value))
  }

  if (authorsToShow.length === 0) return

  // Fetch real daily author data
  let dailyAuthorData: any[] = []
  try {
    const response = await api.get(`/repositories/${repoId}/stats/daily-authors`, {
      params: { 
        days: selectedDays.value,
        exclude_ai: excludeAI.value
      }
    })
    dailyAuthorData = response.data.daily_stats || []
  } catch (error) {
    console.error('Failed to fetch daily author data for chart:', error)
    return
  }

  // Create date range for labels
  const dateRange: string[] = []
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

  // Create datasets for each author using real daily data
  const datasets = authorsToShow.map((author, index) => {
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
    
    // Get real daily lines added data for this author
    const dailyActivity = dateRange.map(date => {
      const dayData = dailyAuthorData.find(d => d.date === date)
      if (!dayData || !dayData.authors) return 0
      
      const authorData = dayData.authors.find((a: any) => a.author.email === author.author_email)
      return authorData ? authorData.added_lines : 0
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
          text: `Author Code Added Over Time - ${repository.value?.name || 'Repository'}`,
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
              return `${authorName}: ${value.toLocaleString()} lines added`
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
    // Check if we already have the data cached
    if (dailyAuthorDetails.value.has(date)) return
    
    // Fetch real daily author breakdown from API
    const response = await api.get(`/repositories/${repoId}/stats/daily-authors`, {
      params: { 
        days: selectedDays.value,
        exclude_ai: excludeAI.value
      }
    })
    
    const dailyBreakdown = response.data.daily_stats || []
    
    // Process the response and cache all daily data
    dailyBreakdown.forEach((dayStats: any) => {
      const dayDate = dayStats.date
      const authorsForDay: DailyAuthorDetail[] = []
      
      if (dayStats.authors && dayStats.authors.length > 0) {
        dayStats.authors.forEach((authorDetail: any) => {
          authorsForDay.push({
            author_email: authorDetail.author.email,
            author_name: authorDetail.author.name,
            is_ai_coder: authorDetail.author.is_ai_coder || false,
            commits_count: authorDetail.commits_count,
            added_lines: authorDetail.added_lines,
            deleted_lines: authorDetail.deleted_lines,
            files_changed: authorDetail.files_changed
          })
        })
      }
      
      // Cache the data for this date
      dailyAuthorDetails.value.set(dayDate, authorsForDay)
    })
  } catch (err) {
    console.error('Failed to fetch daily author details:', err)
    // Fallback: if API fails, show empty details for this date
    dailyAuthorDetails.value.set(date, [])
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