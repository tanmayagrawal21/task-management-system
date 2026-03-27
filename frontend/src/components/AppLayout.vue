<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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
      <span class="font-semibold text-gray-800 text-base">Task Manager</span>
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-600 hidden sm:block">{{ auth.user?.name }}</span>
        <Button
          label="Sign out"
          severity="secondary"
          size="small"
          text
          @click="logout"
        />
      </div>
    </header>

    <main class="flex-1 p-4 md:p-8">
      <slot />
    </main>
  </div>
</template>
