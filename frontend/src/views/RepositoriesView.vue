<template>
  <AppLayout>
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold text-gray-900">Repositories</h1>
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
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useApi } from '@/composables/useApi'

interface Repository {
  id: number
  name: string
  local_path: string
  description?: string
  last_analyzed_at: string | null
}

const { api, loading, error } = useApi()
const repositories = ref<Repository[]>([])
const showAddForm = ref(false)
const adding = ref(false)
const analyzingRepo = ref<number | null>(null)
const deletingRepo = ref<number | null>(null)
const analyzingAll = ref(false)

const newRepo = reactive({
  name: '',
  local_path: '',
  description: '',
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
  } catch (err) {
    console.error('Failed to delete repository:', err)
  } finally {
    deletingRepo.value = null
  }
}

onMounted(fetchRepositories)
</script>