import { ref } from 'vue'
import Anthropic from '@anthropic-ai/sdk'
import OpenAI from 'openai'
import { GoogleGenerativeAI } from '@google/generative-ai'
import { useTasksStore } from '@/stores/tasks'
import { useAuthStore } from '@/stores/auth'

export type Provider = 'claude' | 'openai' | 'gemini'

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

const STORAGE_KEY_PROVIDER = 'ai_provider'
const STORAGE_KEY_KEY = 'ai_api_key'
const STORAGE_KEY_MESSAGES = 'ai_messages'

const TOOL_DEFINITIONS = [
  {
    name: 'create_task',
    description: 'Create a new task',
    input_schema: {
      type: 'object',
      properties: {
        title: { type: 'string', description: 'Task title' },
        description: { type: 'string', description: 'Optional description' },
        status: { type: 'string', enum: ['Todo', 'In Progress', 'Done'], description: 'Task status' },
        assigned_user_id: { type: 'number', description: 'User id to assign to (optional)' },
      },
      required: ['title', 'status'],
    },
  },
  {
    name: 'update_task',
    description: 'Update an existing task. Only the creator or assignee can update.',
    input_schema: {
      type: 'object',
      properties: {
        id: { type: 'number', description: 'Task id' },
        title: { type: 'string' },
        description: { type: 'string' },
        status: { type: 'string', enum: ['Todo', 'In Progress', 'Done'] },
        assigned_user_id: { type: 'number', description: 'User id to assign to, or null to unassign' },
      },
      required: ['id'],
    },
  },
  {
    name: 'claim_task',
    description: 'Claim an unassigned task for yourself',
    input_schema: {
      type: 'object',
      properties: {
        id: { type: 'number', description: 'Task id' },
      },
      required: ['id'],
    },
  },
  {
    name: 'delete_task',
    description: 'Delete a task. Only the creator can delete.',
    input_schema: {
      type: 'object',
      properties: {
        id: { type: 'number', description: 'Task id' },
      },
      required: ['id'],
    },
  },
]

function buildSystemPrompt(tasks: any[], users: any[], currentUser: any): string {
  const taskList = tasks.map(t =>
    `- [id:${t.id}] "${t.title}" | status: ${t.status} | assigned: ${t.assigned_user?.name ?? 'unassigned'} | created by: ${t.created_by?.name ?? 'unknown'}`
  ).join('\n')

  const userList = users.map(u => `- [id:${u.id}] ${u.name} (${u.email})`).join('\n')

  return `You are a task management assistant embedded in a task tracker.
Your responses are displayed in a chat UI that renders Markdown, so you may use **bold**, bullet lists, and other Markdown formatting where it helps readability. Keep responses concise — avoid long prose.

Current user: ${currentUser.name} (id: ${currentUser.id}, email: ${currentUser.email})

Users in the system:
${userList}

Current tasks:
${taskList}

You can use tools to create, update, claim, or delete tasks on behalf of the current user.
Permission rules (enforced by the API — if you violate them you will get an error):
- Anyone can create tasks and claim unassigned tasks
- Only the creator or current assignee can update a task
- Only the creator can delete a task

When asked to make changes, use the appropriate tool. Confirm what you did after each action.`
}

async function executeTool(name: string, input: any, store: ReturnType<typeof useTasksStore>): Promise<string> {
  try {
    if (name === 'create_task') {
      await store.createTask(input)
      return `Created task "${input.title}"`
    }
    if (name === 'update_task') {
      const { id, ...data } = input
      await store.updateTask(id, data)
      return `Updated task ${id}`
    }
    if (name === 'claim_task') {
      await store.claimTask(input.id)
      return `Claimed task ${input.id}`
    }
    if (name === 'delete_task') {
      await store.deleteTask(input.id)
      return `Deleted task ${input.id}`
    }
    return 'Unknown tool'
  } catch (e: any) {
    return `Error: ${e?.response?.data?.detail ?? e?.message ?? 'unknown error'}`
  }
}

// Convert our tool definitions to OpenAI/Gemini format
function toOpenAiTools() {
  return TOOL_DEFINITIONS.map(t => ({
    type: 'function' as const,
    function: {
      name: t.name,
      description: t.description,
      parameters: t.input_schema,
    },
  }))
}

export function useAiChat() {
  const stored = localStorage.getItem(STORAGE_KEY_MESSAGES)
  const messages = ref<Message[]>(stored ? JSON.parse(stored) : [])
  const loading = ref(false)
  const error = ref('')
  const provider = ref<Provider>((localStorage.getItem(STORAGE_KEY_PROVIDER) as Provider) || 'claude')
  const apiKey = ref(localStorage.getItem(STORAGE_KEY_KEY) || '')

  function persistMessages() {
    localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages.value))
  }

  function saveSettings(p: Provider, key: string) {
    provider.value = p
    apiKey.value = key
    localStorage.setItem(STORAGE_KEY_PROVIDER, p)
    localStorage.setItem(STORAGE_KEY_KEY, key)
  }

  function clearHistory() {
    messages.value = []
    localStorage.removeItem(STORAGE_KEY_MESSAGES)
  }

  async function sendMessage(userText: string) {
    if (!apiKey.value) {
      error.value = 'No API key set. Open settings to add one.'
      return
    }

    messages.value.push({ role: 'user', content: userText })
    loading.value = true
    error.value = ''

    const store = useTasksStore()
    const auth = useAuthStore()
    const systemPrompt = buildSystemPrompt(store.tasks, store.users, auth.user)

    try {
      if (provider.value === 'claude') {
        await runClaude(systemPrompt, store)
      } else if (provider.value === 'openai') {
        await runOpenAi(systemPrompt, store)
      } else {
        await runGemini(systemPrompt, store)
      }
    } catch (e: any) {
      error.value = e?.message ?? 'Something went wrong'
      messages.value.pop() // remove the user message on hard error
    } finally {
      loading.value = false
    }
  }

  async function runClaude(systemPrompt: string, store: ReturnType<typeof useTasksStore>) {
    const client = new Anthropic({ apiKey: apiKey.value, dangerouslyAllowBrowser: true })

    // Build a local mutable history for the agentic loop
    const apiMessages: any[] = messages.value.map(m => ({ role: m.role, content: m.content }))

    let response = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 1024,
      system: systemPrompt,
      tools: TOOL_DEFINITIONS as any,
      messages: apiMessages,
    })

    // Agentic loop: keep going while model wants to use tools
    while (response.stop_reason === 'tool_use') {
      // Append assistant turn (may contain text + multiple tool_use blocks)
      apiMessages.push({ role: 'assistant', content: response.content })

      // Execute ALL tool_use blocks and collect results
      const toolUseBlocks = response.content.filter(b => b.type === 'tool_use') as any[]
      const toolResults = await Promise.all(
        toolUseBlocks.map(async (block) => ({
          type: 'tool_result',
          tool_use_id: block.id,
          content: await executeTool(block.name, block.input, store),
        }))
      )

      // Return all results in a single user message
      apiMessages.push({ role: 'user', content: toolResults })

      response = await client.messages.create({
        model: 'claude-opus-4-6',
        max_tokens: 1024,
        system: systemPrompt,
        tools: TOOL_DEFINITIONS as any,
        messages: apiMessages,
      })
    }

    const text = response.content.find(b => b.type === 'text') as any
    messages.value.push({ role: 'assistant', content: text?.text ?? '(no response)' })
    persistMessages()
  }

  async function runOpenAi(systemPrompt: string, store: ReturnType<typeof useTasksStore>) {
    const client = new OpenAI({ apiKey: apiKey.value, dangerouslyAllowBrowser: true })

    const history: OpenAI.ChatCompletionMessageParam[] = [
      { role: 'system', content: systemPrompt },
      ...messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content } as OpenAI.ChatCompletionMessageParam)),
      { role: 'user', content: messages.value[messages.value.length - 1].content },
    ]

    let response = await client.chat.completions.create({
      model: 'gpt-4o',
      tools: toOpenAiTools(),
      messages: history,
    })

    let msg = response.choices[0].message
    history.push(msg)

    while (msg.tool_calls?.length) {
      for (const call of msg.tool_calls) {
        const fn = (call as any).function
        const result = await executeTool(fn.name, JSON.parse(fn.arguments), store)
        history.push({ role: 'tool', tool_call_id: call.id, content: result })
      }
      response = await client.chat.completions.create({ model: 'gpt-4o', tools: toOpenAiTools(), messages: history })
      msg = response.choices[0].message
      history.push(msg)
    }

    messages.value.push({ role: 'assistant', content: msg.content ?? '(no response)' })
    persistMessages()
  }

  async function runGemini(systemPrompt: string, store: ReturnType<typeof useTasksStore>) {
    const genAI = new GoogleGenerativeAI(apiKey.value)
    const model = genAI.getGenerativeModel({
      model: 'gemini-1.5-pro',
      systemInstruction: systemPrompt,
      tools: [{
        functionDeclarations: TOOL_DEFINITIONS.map(t => ({
          name: t.name,
          description: t.description,
          parameters: t.input_schema as any,
        })),
      }],
    })

    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    }))

    const chat = model.startChat({ history })
    let result = await chat.sendMessage(messages.value[messages.value.length - 1].content)

    while (result.response.functionCalls()?.length) {
      const calls = result.response.functionCalls()!
      const toolResponses = await Promise.all(
        calls.map(async call => ({
          functionResponse: {
            name: call.name,
            response: { result: await executeTool(call.name, call.args, store) },
          },
        }))
      )
      result = await chat.sendMessage(toolResponses as any)
    }

    messages.value.push({ role: 'assistant', content: result.response.text() })
    persistMessages()
  }

  return { messages, loading, error, provider, apiKey, saveSettings, clearHistory, sendMessage }
}
