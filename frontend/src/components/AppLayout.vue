<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { RouterLink } from 'vue-router'
import Button from 'primevue/button'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <header class="bg-white border-b border-gray-200 px-4 md:px-8 h-14 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-6">
        <span class="font-semibold text-gray-800 text-base">Task Manager</span>
        <nav class="flex gap-4">
          <RouterLink
            :to="{ name: 'tasks' }"
            class="text-sm font-medium transition-colors text-gray-500 hover:text-gray-800"
            active-class="text-blue-600"
          >
            Tasks
          </RouterLink>
          <RouterLink
            :to="{ name: 'users' }"
            class="text-sm font-medium transition-colors text-gray-500 hover:text-gray-800"
            active-class="text-blue-600"
          >
            Users
          </RouterLink>
        </nav>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-600 hidden sm:block">{{ auth.user?.name }}</span>
        <Button label="Sign out" severity="secondary" size="small" text @click="logout" />
      </div>
    </header>

    <main class="flex-1 p-4 md:p-8">
      <slot />
    </main>
  </div>
</template>
