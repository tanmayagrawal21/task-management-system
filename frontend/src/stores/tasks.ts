import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export type TaskStatus = 'Todo' | 'In Progress' | 'Done'

export interface User {
  id: number
  name: string
  email: string
}

export interface Task {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  assigned_user_id: number | null
  assigned_user: User | null
  created_by_id: number | null
  created_by: User | null
  created_at: string
  updated_at: string
}

export interface TaskFilters {
  status?: TaskStatus | null
  assigned_user_id?: number | null
}

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const total = ref(0)
  const totalPages = ref(1)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const filters = ref<TaskFilters>({})

  const users = ref<User[]>([])

  async function fetchTasks() {
    loading.value = true
    try {
      const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.assigned_user_id) params.assigned_user_id = filters.value.assigned_user_id

      const res = await api.get('/tasks', { params })
      tasks.value = res.data.items
      total.value = res.data.total
      totalPages.value = res.data.total_pages
    } finally {
      loading.value = false
    }
  }

  async function fetchUsers() {
    const res = await api.get('/users')
    users.value = res.data
  }

  async function createTask(data: { title: string; description?: string | null; status: TaskStatus; assigned_user_id?: number | null }) {
    await api.post('/tasks', data)
    await fetchTasks()
  }

  async function updateTask(id: number, data: Partial<{ title: string; description: string | null; status: TaskStatus; assigned_user_id: number | null }>) {
    await api.put(`/tasks/${id}`, data)
    await fetchTasks()
  }

  async function claimTask(id: number) {
    await api.post(`/tasks/${id}/claim`)
    await fetchTasks()
  }

  async function deleteTask(id: number) {
    await api.delete(`/tasks/${id}`)
    await fetchTasks()
  }

  function setPage(p: number) {
    page.value = p
    fetchTasks()
  }

  function setFilters(f: TaskFilters) {
    filters.value = f
    page.value = 1
    fetchTasks()
  }

  return { tasks, total, totalPages, page, pageSize, loading, filters, users, fetchTasks, fetchUsers, createTask, updateTask, claimTask, deleteTask, setPage, setFilters }
})
