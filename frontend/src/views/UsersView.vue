<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Skeleton from 'primevue/skeleton'

interface User {
  id: number
  name: string
  email: string
  created_at: string
}

const users = ref<User[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/users')
    users.value = res.data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppLayout>
    <div class="max-w-3xl mx-auto">
      <h1 class="text-xl font-bold text-gray-800 mb-6">Users</h1>

      <div v-if="loading" class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div v-for="i in 4" :key="i" class="flex gap-4 px-4 py-3 border-b border-gray-100 last:border-0">
          <Skeleton width="30%" height="1.2rem" />
          <Skeleton width="40%" height="1.2rem" />
          <Skeleton width="20%" height="1.2rem" />
        </div>
      </div>

      <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <DataTable :value="users" class="text-sm">
          <template #empty>
            <div class="text-center py-10 text-gray-400">No users found</div>
          </template>
          <Column field="name" header="Name" />
          <Column field="email" header="Email">
            <template #body="{ data }">
              <span class="text-gray-600">{{ data.email }}</span>
            </template>
          </Column>
          <Column field="created_at" header="Joined" style="width: 140px">
            <template #body="{ data }">
              <span class="text-gray-500">{{ new Date(data.created_at).toLocaleDateString() }}</span>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </AppLayout>
</template>
