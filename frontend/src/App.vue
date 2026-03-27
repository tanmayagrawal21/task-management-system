<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue'

const crashed = ref(false)

onErrorCaptured((err) => {
  console.error('Unhandled error:', err)
  crashed.value = true
  return false
})

function reload() {
  crashed.value = false
  location.reload()
}
</script>

<template>
  <div v-if="crashed" class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white rounded-xl shadow p-8 text-center max-w-sm">
      <i class="pi pi-exclamation-circle text-4xl text-red-400 mb-4 block" />
      <h1 class="text-lg font-semibold text-gray-800 mb-2">Something went wrong</h1>
      <p class="text-sm text-gray-500 mb-4">An unexpected error occurred. Try refreshing the page.</p>
      <button class="text-sm text-blue-600 hover:underline" @click="reload">Refresh</button>
    </div>
  </div>
  <RouterView v-else />
</template>
