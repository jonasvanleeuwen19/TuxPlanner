<template>
  <div class="p-4 md:p-6 max-w-4xl mx-auto">
    <!-- Greeting + Clock -->
    <div class="mb-6 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ greeting }} 👋</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{{ dateLabel }}</p>
      </div>
      <div class="flex items-center gap-2 text-3xl font-mono font-bold text-blue-500 dark:text-blue-400">
        <i class="mdi mdi-clock-outline text-2xl" />
        {{ clockStr }}
      </div>
    </div>

    <!-- Cards row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Events today -->
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 flex flex-col">
        <div class="flex items-center mb-3">
          <div class="w-8 h-8 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-2 shrink-0">
            <i class="mdi mdi-calendar text-blue-500 dark:text-blue-400" />
          </div>
          <span class="text-sm font-semibold text-gray-800 dark:text-gray-200">Events Today</span>
          <span class="ml-auto text-xs font-medium text-blue-500 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-0.5 rounded-full">{{ todayEvents.length }}</span>
        </div>
        <div v-if="loading" class="flex justify-center py-4">
          <i class="mdi mdi-loading animate-spin text-2xl text-blue-400" />
        </div>
        <div v-else-if="todayEvents.length === 0" class="text-xs text-gray-400 dark:text-gray-500 py-2">No events scheduled for today</div>
        <div v-else class="flex flex-col gap-2 flex-1">
          <div
            v-for="event in todayEvents"
            :key="event.id"
            class="flex items-start gap-2 p-2 rounded-xl bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30"
          >
            <div class="w-1.5 h-full min-h-[1.5rem] rounded-full shrink-0 mt-0.5" :style="{ backgroundColor: event.color || '#3b82f6' }" />
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">{{ event.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatEventTime(event) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tasks today -->
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 flex flex-col">
        <div class="flex items-center mb-3">
          <div class="w-8 h-8 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mr-2 shrink-0">
            <i class="mdi mdi-checkbox-marked-circle-outline text-amber-500 dark:text-amber-400" />
          </div>
          <span class="text-sm font-semibold text-gray-800 dark:text-gray-200">Tasks Today</span>
          <span class="ml-auto text-xs font-medium text-amber-500 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-2 py-0.5 rounded-full">{{ todayTasks.length }}</span>
        </div>
        <div v-if="loading" class="flex justify-center py-4">
          <i class="mdi mdi-loading animate-spin text-2xl text-amber-400" />
        </div>
        <div v-else-if="todayTasks.length === 0" class="text-xs text-gray-400 dark:text-gray-500 py-2">No tasks due today</div>
        <div v-else class="flex flex-col gap-2 flex-1">
          <div
            v-for="task in todayTasks"
            :key="task.id"
            class="flex items-center gap-2 p-2 rounded-xl bg-amber-50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-900/30"
          >
            <i :class="['mdi text-sm shrink-0', task.completed ? 'mdi-check-circle text-green-500' : 'mdi-circle-outline text-amber-400']" />
            <p :class="['text-xs font-medium truncate flex-1', task.completed ? 'line-through text-gray-400 dark:text-gray-600' : 'text-gray-800 dark:text-gray-200']">{{ task.title }}</p>
            <span v-if="task.priority" :class="['text-xs px-1.5 py-0.5 rounded font-medium shrink-0', priorityClass(task.priority)]">{{ task.priority }}</span>
          </div>
        </div>
      </div>

      <!-- Sessions today -->
      <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 flex flex-col">
        <div class="flex items-center mb-3">
          <div class="w-8 h-8 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-2 shrink-0">
            <i class="mdi mdi-calendar-clock text-purple-500 dark:text-purple-400" />
          </div>
          <span class="text-sm font-semibold text-gray-800 dark:text-gray-200">Sessions Today</span>
          <span class="ml-auto text-xs font-medium text-purple-500 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 px-2 py-0.5 rounded-full">{{ todaySessions.length }}</span>
        </div>
        <div v-if="loading" class="flex justify-center py-4">
          <i class="mdi mdi-loading animate-spin text-2xl text-purple-400" />
        </div>
        <div v-else-if="todaySessions.length === 0" class="text-xs text-gray-400 dark:text-gray-500 py-2">No work sessions planned for today</div>
        <div v-else class="flex flex-col gap-2 flex-1">
          <div
            v-for="session in todaySessions"
            :key="session.id"
            class="flex items-start gap-2 p-2 rounded-xl bg-purple-50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-900/30"
          >
            <i class="mdi mdi-calendar-clock text-sm text-purple-400 dark:text-purple-500 mt-0.5 shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">{{ session.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatEventTime(session) }}</p>
              <p v-if="session.description" class="text-xs text-gray-400 dark:text-gray-500 truncate mt-0.5">{{ session.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { eventsApi, todosApi } from '../api/index.js'

const now = ref(new Date())
let clockInterval = null

onMounted(() => {
  clockInterval = setInterval(() => { now.value = new Date() }, 1000)
  fetchData()
})

onUnmounted(() => {
  clearInterval(clockInterval)
})

const clockStr = computed(() => {
  return now.value.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
})

const dateLabel = computed(() =>
  now.value.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
)

const greeting = computed(() => {
  const h = now.value.getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})

const loading = ref(false)
const allEvents = ref([])
const allTodos = ref([])

async function fetchData() {
  loading.value = true
  try {
    const start = new Date()
    start.setHours(0, 0, 0, 0)
    const end = new Date()
    end.setHours(23, 59, 59, 999)

    const [eventsRes, todosRes] = await Promise.all([
      eventsApi.list({ start: start.toISOString(), end: end.toISOString() }),
      todosApi.list(),
    ])
    allEvents.value = eventsRes.data
    allTodos.value = todosRes.data
  } catch (err) {
    console.error('Failed to fetch home page data', err)
  } finally {
    loading.value = false
  }
}

const todayEvents = computed(() =>
  allEvents.value.filter((e) => e.source !== 'task_session')
)

const todaySessions = computed(() =>
  allEvents.value.filter((e) => e.source === 'task_session')
)

const todayTasks = computed(() => {
  const todayStr = now.value.toISOString().slice(0, 10)
  return allTodos.value.filter((t) => t.due_date && t.due_date.slice(0, 10) === todayStr)
})

function formatEventTime(event) {
  if (event.all_day) return 'All day'
  const start = event.start ? new Date(event.start).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) : ''
  const end = event.end ? new Date(event.end).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) : ''
  if (start && end) return `${start} – ${end}`
  return start
}

function priorityClass(priority) {
  if (priority === 'high') return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
  if (priority === 'medium') return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
  return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
}
</script>
