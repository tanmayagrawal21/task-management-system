<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Email and password are required.'
    return
  }

  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'tasks' })
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white rounded-xl shadow-md p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-gray-800 mb-1">Task Manager</h1>
      <p class="text-sm text-gray-500 mb-6">Sign in to your account</p>

      <Message v-if="error" severity="error" class="mb-4">{{ error }}</Message>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">Email</label>
          <InputText
            v-model="email"
            type="email"
            placeholder="you@example.com"
            class="w-full"
            autocomplete="email"
          />
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">Password</label>
          <Password
            v-model="password"
            placeholder="••••••••"
            :feedback="false"
            toggle-mask
            input-class="w-full"
            class="w-full"
            autocomplete="current-password"
          />
        </div>

        <Button
          type="submit"
          label="Sign in"
          class="w-full mt-2"
          :loading="loading"
        />
      </form>
    </div>
  </div>
</template>
