<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from 'primevue/button'

const auth = useAuthStore()
const router = useRouter()
const mobileNavOpen = ref(false)

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}

function closeNav() {
  mobileNavOpen.value = false
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <header class="bg-white border-b border-gray-200 px-4 md:px-8 h-14 flex items-center justify-between shrink-0 relative z-20">
      <div class="flex items-center gap-6">
        <span class="font-semibold text-gray-800 text-base">Task Manager</span>
        <!-- Desktop nav -->
        <nav class="hidden sm:flex gap-4">
          <RouterLink
            :to="{ name: 'tasks' }"
            class="text-sm font-medium transition-colors text-gray-500 hover:text-gray-800"
            active-class="!text-blue-600"
            @click="closeNav"
          >
            Tasks
          </RouterLink>
          <RouterLink
            :to="{ name: 'users' }"
            class="text-sm font-medium transition-colors text-gray-500 hover:text-gray-800"
            active-class="!text-blue-600"
            @click="closeNav"
          >
            Users
          </RouterLink>
        </nav>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600 hidden sm:block">{{ auth.user?.name }}</span>
        <Button label="Sign out" severity="secondary" size="small" text class="hidden sm:inline-flex" @click="logout" />
        <!-- Hamburger -->
        <button
          class="sm:hidden p-2 rounded-md text-gray-500 hover:text-gray-800 hover:bg-gray-100"
          @click="mobileNavOpen = !mobileNavOpen"
        >
          <i :class="mobileNavOpen ? 'pi pi-times' : 'pi pi-bars'" class="text-lg" />
        </button>
      </div>
    </header>

    <!-- Mobile nav drawer -->
    <div
      v-if="mobileNavOpen"
      class="sm:hidden bg-white border-b border-gray-200 px-4 py-3 flex flex-col gap-1 z-10"
    >
      <span class="text-xs text-gray-400 mb-1">{{ auth.user?.name }}</span>
      <RouterLink
        :to="{ name: 'tasks' }"
        class="text-sm font-medium py-2 text-gray-700 hover:text-blue-600"
        active-class="text-blue-600"
        @click="closeNav"
      >
        Tasks
      </RouterLink>
      <RouterLink
        :to="{ name: 'users' }"
        class="text-sm font-medium py-2 text-gray-700 hover:text-blue-600"
        active-class="text-blue-600"
        @click="closeNav"
      >
        Users
      </RouterLink>
      <button class="text-sm font-medium py-2 text-left text-red-500 hover:text-red-700" @click="logout">
        Sign out
      </button>
    </div>

    <main class="flex-1 p-4 md:p-8">
      <slot />
    </main>
  </div>
</template>
