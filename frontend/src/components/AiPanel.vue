<template>
  <div
    class="fixed top-0 right-0 h-full w-full sm:w-96 bg-white shadow-2xl border-l border-gray-200 flex flex-col z-40 transition-transform duration-300"
    :class="open ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center gap-2">
        <span class="text-lg">✦</span>
        <span class="font-semibold text-gray-800">AI Assistant</span>
        <span class="text-xs text-gray-400 uppercase tracking-wide">{{ chat.provider.value }}</span>
      </div>
      <div class="flex items-center gap-2">
        <Button icon="pi pi-cog" text rounded size="small" @click="settingsVisible = true" />
        <Button icon="pi pi-times" text rounded size="small" @click="$emit('close')" />
      </div>
    </div>

    <!-- Disclaimer -->
    <div class="px-4 py-2 bg-gray-50 border-b border-gray-200 text-xs text-gray-400 text-center">
      API keys and conversation history are stored in your browser only and never sent to our servers.
    </div>

    <!-- No key warning -->
    <div v-if="!chat.apiKey.value" class="m-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
      No API key set.
      <button class="underline font-medium ml-1" @click="settingsVisible = true">Open settings</button>
      to get started.
    </div>

    <!-- Messages -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto px-4 py-3 space-y-3">
      <div v-if="chat.messages.value.length === 0" class="text-center text-gray-400 text-sm mt-8">
        <p class="text-2xl mb-2">✦</p>
        <p>Ask me about your tasks or tell me to make changes.</p>
        <p class="mt-1 text-xs">e.g. "What's unassigned?" or "Mark task 3 as done"</p>
      </div>

      <div
        v-for="(msg, i) in chat.messages.value"
        :key="i"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed"
          :class="msg.role === 'user'
            ? 'bg-blue-500 text-white rounded-br-sm whitespace-pre-wrap'
            : 'bg-gray-100 text-gray-800 rounded-bl-sm prose prose-sm max-w-none'"
          v-html="msg.role === 'assistant' ? marked.parse(msg.content) : msg.content"
        />
      </div>

      <div v-if="chat.loading.value" class="flex justify-start">
        <div class="bg-gray-100 rounded-2xl rounded-bl-sm px-3 py-2">
          <span class="inline-flex gap-1">
            <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0ms" />
            <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:150ms" />
            <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:300ms" />
          </span>
        </div>
      </div>

      <div v-if="chat.error.value" class="text-xs text-red-500 text-center">
        {{ chat.error.value }}
      </div>
    </div>

    <!-- Input -->
    <div class="px-4 py-3 border-t border-gray-200 flex gap-2">
      <InputText
        v-model="input"
        placeholder="Ask or instruct..."
        class="flex-1 text-sm"
        :disabled="chat.loading.value"
        @keydown.enter.exact.prevent="submit"
      />
      <Button
        icon="pi pi-send"
        :disabled="!input.trim() || chat.loading.value"
        @click="submit"
      />
    </div>

    <!-- Settings dialog -->
    <Dialog v-model:visible="settingsVisible" header="AI Settings" modal :style="{ width: '22rem' }">
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">Provider</label>
          <Select
            v-model="draftProvider"
            :options="providerOptions"
            option-label="label"
            option-value="value"
          />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">API Key</label>
          <InputText v-model="draftKey" type="password" placeholder="Paste your API key" class="font-mono text-sm" />
          <span class="text-xs text-gray-400">Stored in localStorage only — never sent to our server.</span>
        </div>
        <div class="flex justify-between items-center">
          <Button label="Clear history" text size="small" severity="secondary" @click="chat.clearHistory()" />
          <Button label="Save" @click="saveSettings" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { marked } from 'marked'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Dialog from 'primevue/dialog'
import { useAiChat, type Provider } from '@/composables/useAiChat'

defineProps<{ open: boolean }>()
defineEmits<{ close: [] }>()

const chat = useAiChat()
const input = ref('')
const settingsVisible = ref(false)
const messagesEl = ref<HTMLElement | null>(null)

const draftProvider = ref<Provider>(chat.provider.value)
const draftKey = ref(chat.apiKey.value)

const providerOptions = [
  { label: 'Claude (Anthropic)', value: 'claude' },
  { label: 'GPT-4o (OpenAI)', value: 'openai' },
  { label: 'Gemini 1.5 Pro (Google)', value: 'gemini' },
]

function saveSettings() {
  chat.saveSettings(draftProvider.value, draftKey.value)
  settingsVisible.value = false
}

async function submit() {
  const text = input.value.trim()
  if (!text || chat.loading.value) return
  input.value = ''
  await chat.sendMessage(text)
}

watch(
  () => chat.messages.value.length,
  async () => {
    await nextTick()
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  }
)
</script>
