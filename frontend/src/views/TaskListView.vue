<script setup lang="ts">
import { onMounted, computed } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useTasksStore, type TaskStatus } from '@/stores/tasks'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'

const store = useTasksStore()

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
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-xl font-bold text-gray-800">Tasks</h1>
        <Button label="New task" icon="pi pi-plus" size="small" disabled />
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 mb-4 flex flex-wrap gap-3 items-center">
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
      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <DataTable
          :value="store.tasks"
          lazy
          paginator
          :rows="store.pageSize"
          :total-records="store.total"
          :first="(store.page - 1) * store.pageSize"
          paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
          :rows-per-page-options="[10, 20, 50]"
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

          <Column field="created_at" header="Created" style="width: 130px">
            <template #body="{ data }">
              <span class="text-gray-500">{{ new Date(data.created_at).toLocaleDateString() }}</span>
            </template>
          </Column>

          <Column style="width: 60px">
            <template #body>
              <Button icon="pi pi-ellipsis-v" severity="secondary" text size="small" rounded disabled />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </AppLayout>
</template>
