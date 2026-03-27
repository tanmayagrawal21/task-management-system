<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Tabs from 'primevue/tabs'
import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'

const auth = useAuthStore()
const router = useRouter()

// Login
const loginEmail = ref('')
const loginPassword = ref('')
const loginError = ref('')
const loginLoading = ref(false)

async function submitLogin() {
  loginError.value = ''
  if (!loginEmail.value || !loginPassword.value) {
    loginError.value = 'Email and password are required.'
    return
  }
  loginLoading.value = true
  try {
    await auth.login(loginEmail.value, loginPassword.value)
    router.push({ name: 'tasks' })
  } catch (e: any) {
    loginError.value = e?.response?.data?.detail ?? 'Login failed. Please try again.'
  } finally {
    loginLoading.value = false
  }
}

// Register
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regConfirm = ref('')
const regError = ref('')
const regLoading = ref(false)

async function submitRegister() {
  regError.value = ''
  if (!regName.value || !regEmail.value || !regPassword.value || !regConfirm.value) {
    regError.value = 'All fields are required.'
    return
  }
  if (regPassword.value !== regConfirm.value) {
    regError.value = 'Passwords do not match.'
    return
  }
  if (regPassword.value.length < 8) {
    regError.value = 'Password must be at least 8 characters.'
    return
  }
  regLoading.value = true
  try {
    const res = await api.post('/auth/register', {
      name: regName.value,
      email: regEmail.value,
      password: regPassword.value,
    })
    auth.setSession(res.data.access_token, res.data.user)
    router.push({ name: 'tasks' })
  } catch (e: any) {
    regError.value = e?.response?.data?.detail ?? 'Registration failed. Please try again.'
  } finally {
    regLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white rounded-xl shadow-md p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-gray-800 mb-1">Task Manager</h1>
      <p class="text-sm text-gray-500 mb-5">Manage your team's work in one place</p>

      <Tabs value="login">
        <TabList>
          <Tab value="login">Sign in</Tab>
          <Tab value="register">Create account</Tab>
        </TabList>

        <TabPanels>
          <!-- Login -->
          <TabPanel value="login">
            <Message v-if="loginError" severity="error" class="mb-4 mt-3">{{ loginError }}</Message>
            <form class="flex flex-col gap-4 mt-3" @submit.prevent="submitLogin">
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">Email</label>
                <InputText v-model="loginEmail" type="email" placeholder="you@example.com" class="w-full" autocomplete="email" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">Password</label>
                <Password v-model="loginPassword" placeholder="••••••••" :feedback="false" toggle-mask input-class="w-full" class="w-full" autocomplete="current-password" />
              </div>
              <Button type="submit" label="Sign in" class="w-full mt-1" :loading="loginLoading" />
            </form>
          </TabPanel>

          <!-- Register -->
          <TabPanel value="register">
            <Message v-if="regError" severity="error" class="mb-4 mt-3">{{ regError }}</Message>
            <form class="flex flex-col gap-4 mt-3" @submit.prevent="submitRegister">
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">Full name</label>
                <InputText v-model="regName" placeholder="Jane Doe" class="w-full" autocomplete="name" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">Email</label>
                <InputText v-model="regEmail" type="email" placeholder="you@example.com" class="w-full" autocomplete="email" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">Password</label>
                <Password v-model="regPassword" placeholder="Min. 8 characters" :feedback="false" toggle-mask input-class="w-full" class="w-full" autocomplete="new-password" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-gray-700">Confirm password</label>
                <Password v-model="regConfirm" placeholder="Repeat password" :feedback="false" toggle-mask input-class="w-full" class="w-full" autocomplete="new-password" />
              </div>
              <Button type="submit" label="Create account" class="w-full mt-1" :loading="regLoading" />
            </form>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
  </div>
</template>
