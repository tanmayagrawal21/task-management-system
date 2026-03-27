<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import TaskForm from '@/components/TaskForm.vue'
import AiPanel from '@/components/AiPanel.vue'
import { useTasksStore, type TaskStatus, type Task } from '@/stores/tasks'
import { useAuthStore } from '@/stores/auth'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const store = useTasksStore()
const auth = useAuthStore()
const confirm = useConfirm()
const toast = useToast()

const formVisible = ref(false)
const editingTask = ref<Task | null>(null)
const aiPanelOpen = ref(false)

const statusOptions = [
  { label: 'All statuses', value: null },
  { label: 'Todo', value: 'Todo' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Done', value: 'Done' },
]

const userOptions = computed(() => [
  { label: 'All users', value: null },
  ...store.users.map((u) => ({ label: u.name, value: u.id })),
])

const selectedStatus = computed({
  get: () => store.filters.status ?? null,
  set: (v) => store.setFilters({ ...store.filters, status: v as TaskStatus | null }),
})

const selectedUser = computed({
  get: () => store.filters.assigned_user_id ?? null,
  set: (v) => store.setFilters({ ...store.filters, assigned_user_id: v as number | null }),
})

function statusSeverity(status: TaskStatus) {
  if (status === 'Done') return 'success'
  if (status === 'In Progress') return 'warn'
  return 'secondary'
}

function canEdit(task: Task) {
  const uid = auth.user?.id
  return uid === task.created_by_id || uid === task.assigned_user_id
}

function canClaim(task: Task) {
  return task.assigned_user_id === null && auth.user?.id !== task.created_by_id
}

function canDelete(task: Task) {
  return auth.user?.id === task.created_by_id
}

function openCreate() {
  editingTask.value = null
  formVisible.value = true
}

function openEdit(task: Task) {
  editingTask.value = task
  formVisible.value = true
}

function onSaved() {
  toast.add({ severity: 'success', summary: editingTask.value ? 'Task updated' : 'Task created', life: 3000 })
}

function confirmDelete(task: Task) {
  confirm.require({
    message: `Delete "${task.title}"? This cannot be undone.`,
    header: 'Delete task',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Delete',
    rejectLabel: 'Cancel',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await store.deleteTask(task.id)
        toast.add({ severity: 'success', summary: 'Task deleted', life: 3000 })
      } catch {
        toast.add({ severity: 'error', summary: 'Failed to delete task', life: 4000 })
      }
    },
  })
}

async function claimTask(task: Task) {
  try {
    await store.claimTask(task.id)
    toast.add({ severity: 'success', summary: 'Task assigned to you', life: 3000 })
  } catch (e: any) {
    toast.add({ severity: 'error', summary: e?.response?.data?.detail ?? 'Failed to claim task', life: 4000 })
  }
}

function onPageChange(event: { page: number }) {
  store.setPage(event.page + 1)
}

function clearFilters() {
  store.setFilters({})
}

onMounted(async () => {
  await Promise.all([store.fetchUsers(), store.fetchTasks()])
})
</script>

<template>
  <AppLayout>
    <Toast />
    <ConfirmDialog />

    <TaskForm v-model:visible="formVisible" :task="editingTask" @saved="onSaved" />
    <AiPanel :open="aiPanelOpen" @close="aiPanelOpen = false" />

    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-xl font-bold text-gray-800">Tasks</h1>
        <div class="flex gap-2">
          <Button icon="pi pi-sparkles" severity="secondary" size="small" outlined @click="aiPanelOpen = !aiPanelOpen" v-tooltip="'AI Assistant'" />
          <Button label="New task" icon="pi pi-plus" size="small" @click="openCreate" />
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 mb-4 flex flex-wrap gap-3 items-center justify-between">
        <Select
          v-model="selectedStatus"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          placeholder="All statuses"
          class="w-44"
        />
        <Select
          v-model="selectedUser"
          :options="userOptions"
          option-label="label"
          option-value="value"
          placeholder="All users"
          class="w-48"
        />
        <Button
          v-if="selectedStatus || selectedUser"
          label="Clear"
          severity="secondary"
          size="small"
          text
          icon="pi pi-times"
          @click="clearFilters"
        />
        <span class="ml-auto text-sm text-gray-500">{{ store.total }} task{{ store.total !== 1 ? 's' : '' }}</span>
      </div>

      <!-- Fetch error -->
      <div v-if="store.fetchError" class="bg-white rounded-xl border border-red-200 p-6 text-center text-red-500 mb-4">
        <i class="pi pi-exclamation-circle text-2xl mb-2 block" />
        {{ store.fetchError }}
        <button class="ml-2 text-sm underline" @click="store.fetchTasks()">Retry</button>
      </div>

      <!-- Loading skeletons -->
      <div v-if="store.loading" class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div v-for="i in 5" :key="i" class="flex gap-4 px-4 py-3 border-b border-gray-100 last:border-0">
          <Skeleton width="40%" height="1.2rem" />
          <Skeleton width="15%" height="1.2rem" />
          <Skeleton width="20%" height="1.2rem" />
          <Skeleton width="15%" height="1.2rem" />
        </div>
      </div>

      <!-- Table -->
      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-x-auto">
        <DataTable
          :value="store.tasks"
          lazy
          paginator
          :rows="store.pageSize"
          :total-records="store.total"
          :first="(store.page - 1) * store.pageSize"
          paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
          class="text-sm"
          @page="onPageChange"
        >
          <template #empty>
            <div class="text-center py-12 text-gray-400">
              <i class="pi pi-inbox text-4xl mb-3 block" />
              No tasks found
            </div>
          </template>

          <Column field="title" header="Title" class="font-medium" />

          <Column field="status" header="Status" style="width: 130px">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="statusSeverity(data.status)" />
            </template>
          </Column>

          <Column field="assigned_user" header="Assignee" style="width: 180px">
            <template #body="{ data }">
              <span v-if="data.assigned_user" class="text-gray-700">{{ data.assigned_user.name }}</span>
              <span v-else class="text-gray-400 italic">Unassigned</span>
            </template>
          </Column>

          <Column field="created_by" header="Creator" style="width: 160px">
            <template #body="{ data }">
              <span v-if="data.created_by" class="text-gray-500 text-xs">{{ data.created_by.name }}</span>
            </template>
          </Column>

          <Column field="created_at" header="Created" style="width: 110px">
            <template #body="{ data }">
              <span class="text-gray-500">{{ new Date(data.created_at).toLocaleDateString() }}</span>
            </template>
          </Column>

          <Column header="" style="width: 120px">
            <template #body="{ data }">
              <div class="flex gap-1 items-center">
                <Button
                  v-if="canClaim(data)"
                  label="Assign to me"
                  size="small"
                  text
                  severity="secondary"
                  class="text-xs"
                  @click="claimTask(data)"
                />
                <Button
                  v-if="canEdit(data)"
                  icon="pi pi-pencil"
                  severity="secondary"
                  text
                  size="small"
                  rounded
                  @click="openEdit(data)"
                />
                <Button
                  v-if="canDelete(data)"
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  size="small"
                  rounded
                  @click="confirmDelete(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </AppLayout>
</template>
