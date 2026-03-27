<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTasksStore, type Task, type TaskStatus } from '@/stores/tasks'
import { useAuthStore } from '@/stores/auth'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'

const props = defineProps<{
  visible: boolean
  task?: Task | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  saved: []
}>()

const store = useTasksStore()
const auth = useAuthStore()

const title = ref('')
const description = ref('')
const taskStatus = ref<TaskStatus>('Todo')
const assignedUserId = ref<number | null>(null)
const error = ref('')
const loading = ref(false)

const isEditing = computed(() => !!props.task)

const statusOptions: { label: string; value: TaskStatus }[] = [
  { label: 'Todo', value: 'Todo' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Done', value: 'Done' },
]

const userOptions = computed(() => [
  { label: 'Unassigned', value: null },
  ...store.users.map((u) => ({ label: u.name, value: u.id })),
])

watch(
  () => props.visible,
  (v) => {
    if (!v) return
    error.value = ''
    if (props.task) {
      title.value = props.task.title
      description.value = props.task.description ?? ''
      taskStatus.value = props.task.status
      assignedUserId.value = props.task.assigned_user_id
    } else {
      title.value = ''
      description.value = ''
      taskStatus.value = 'Todo'
      assignedUserId.value = null
    }
  },
)

function assignToMe() {
  assignedUserId.value = auth.user?.id ?? null
}

function close() {
  emit('update:visible', false)
}

async function submit() {
  error.value = ''
  if (!title.value.trim()) {
    error.value = 'Title is required.'
    return
  }
  loading.value = true
  try {
    const payload = {
      title: title.value.trim(),
      description: description.value.trim() || null,
      status: taskStatus.value,
      assigned_user_id: assignedUserId.value,
    }
    if (props.task) {
      await store.updateTask(props.task.id, payload)
    } else {
      await store.createTask(payload)
    }
    emit('saved')
    close()
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Something went wrong.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    :visible="visible"
    :header="isEditing ? 'Edit task' : 'New task'"
    :style="{ width: 'min(32rem, 95vw)' }"
    :modal="true"
    :draggable="false"
    @update:visible="close"
  >
    <Message v-if="error" severity="error" class="mb-4">{{ error }}</Message>

    <form class="flex flex-col gap-4" @submit.prevent="submit">
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Title <span class="text-red-500">*</span></label>
        <InputText v-model="title" placeholder="Task title" class="w-full" autofocus />
      </div>

      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Description</label>
        <Textarea v-model="description" placeholder="Optional description" :rows="3" class="w-full resize-none" />
      </div>

      <div class="flex gap-3">
        <div class="flex flex-col gap-1 flex-1">
          <label class="text-sm font-medium text-gray-700">Status</label>
          <Select v-model="taskStatus" :options="statusOptions" option-label="label" option-value="value" class="w-full" />
        </div>
        <div class="flex flex-col gap-1 flex-1">
          <label class="text-sm font-medium text-gray-700">Assignee</label>
          <Select v-model="assignedUserId" :options="userOptions" option-label="label" option-value="value" class="w-full" />
          <button
            v-if="assignedUserId !== auth.user?.id"
            type="button"
            class="text-xs text-blue-600 hover:underline text-left mt-0.5"
            @click="assignToMe"
          >
            Assign to me
          </button>
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <Button label="Cancel" severity="secondary" text @click="close" />
        <Button type="submit" :label="isEditing ? 'Save changes' : 'Create task'" :loading="loading" />
      </div>
    </form>
  </Dialog>
</template>
