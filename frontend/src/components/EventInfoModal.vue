<template>
  <Teleport to="body">
    <div
      v-if="modelValue && event"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="close"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3 shrink-0">
          <div
            class="w-3 h-3 rounded-full mr-3 shrink-0"
            :style="{ backgroundColor: event.backgroundColor || '#3b82f6' }"
          />
          <span class="text-base font-bold text-gray-900 dark:text-gray-100 flex-1 min-w-0 truncate">{{ event.title }}</span>
          <div class="flex items-center gap-1 ml-2 shrink-0">
            <button
              v-if="!isIcalEvent"
              class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
              @click="$emit('edit')"
            >
              <i class="mdi mdi-pencil-outline" /> Edit
            </button>
            <button
              class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
              @click="close"
            >
              <i class="mdi mdi-close text-lg" />
            </button>
          </div>
        </div>
        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Scrollable body -->
        <div class="overflow-y-auto flex-1 p-5 space-y-4">
          <!-- iCal badge -->
          <div
            v-if="isIcalEvent"
            class="flex items-center gap-1 px-2 py-0.5 w-fit text-xs rounded-md bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400"
          >
            <i class="mdi mdi-calendar-sync-outline" /> iCal event
          </div>

          <!-- Date/time -->
          <div class="flex items-start gap-2">
            <i class="mdi mdi-clock-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5" />
            <div>
              <p class="text-sm text-gray-900 dark:text-gray-100 font-medium">
                {{ formatEventDate(event) }}
              </p>
              <p v-if="event.allDay" class="text-xs text-gray-500 dark:text-gray-400">All day</p>
            </div>
          </div>

          <!-- Location -->
          <div v-if="eventLocation" class="flex items-start gap-2">
            <i class="mdi mdi-map-marker-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5" />
            <p class="text-sm text-gray-700 dark:text-gray-300">{{ eventLocation }}</p>
          </div>

          <!-- Description -->
          <div v-if="eventDescription" class="flex items-start gap-2">
            <i class="mdi mdi-text-box-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5" />
            <div
              class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm max-w-none dark:prose-invert flex-1"
              v-html="renderedDescription"
            />
          </div>

          <!-- Tasks section -->
          <hr class="border-gray-200 dark:border-gray-700" />
          <div class="flex items-center">
            <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">Tasks</span>
            <div class="flex-1" />
            <button
              class="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
              @click="openAddTask"
            >
              <i class="mdi mdi-plus text-sm" /> Add
            </button>
          </div>

          <div v-if="tasksLoading" class="flex justify-center py-3">
            <i class="mdi mdi-loading animate-spin text-2xl text-blue-500" />
          </div>

          <div v-else class="space-y-1">
            <div
              v-for="task in linkedTasks"
              :key="task.id"
              class="bg-gray-50 dark:bg-gray-800 rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div class="flex items-center gap-2">
                <input
                  type="checkbox"
                  :checked="task.completed"
                  class="w-4 h-4 accent-blue-500 cursor-pointer shrink-0"
                  @change="toggleTask(task)"
                />
                <div class="flex-1 min-w-0">
                  <span
                    class="text-sm"
                    :class="task.completed ? 'line-through text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-gray-100'"
                  >{{ task.title }}</span>
                  <div v-if="task.description" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 whitespace-pre-wrap line-clamp-2">{{ task.description }}</div>
                </div>
                <span
                  v-if="task.priority"
                  :class="['text-xs px-1.5 py-0.5 rounded font-medium shrink-0', priorityClass(task.priority)]"
                >{{ task.priority }}</span>
                <button
                  class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-400 dark:text-gray-500 transition-colors shrink-0"
                  @click="openEditTask(task)"
                >
                  <i class="mdi mdi-pencil-outline text-sm" />
                </button>
                <button
                  class="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors shrink-0"
                  @click="removeTask(task)"
                >
                  <i class="mdi mdi-close text-sm" />
                </button>
              </div>
            </div>
            <p v-if="linkedTasks.length === 0" class="text-sm text-gray-400 dark:text-gray-500 py-1">No tasks yet.</p>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Add / Edit Task Dialog -->
  <TodoDialog
    v-model="taskDialogOpen"
    :todo-lists="todoLists"
    :existing-todos="linkedTasks"
    :edit-todo="editingTask"
    :events="events"
    :linked-event-id="addTaskEventId"
    @save="saveTask"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { todosApi } from '../api/index.js'
import TodoDialog from './TodoDialog.vue'

const props = defineProps({
  modelValue: Boolean,
  event: { type: Object, default: null },
  events: { type: Array, default: () => [] },
  todoLists: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'edit', 'tasks-updated'])

const isIcalEvent = computed(() => props.event?.extendedProps?.source === 'ical')

const eventDescription = computed(() => props.event?.extendedProps?.description || '')
const eventLocation = computed(() => props.event?.extendedProps?.location || '')

const renderedDescription = computed(() => {
  if (!eventDescription.value) return ''
  return DOMPurify.sanitize(marked.parse(eventDescription.value))
})

function formatEventDate(event) {
  if (!event?.start) return ''
  const start = new Date(event.start)
  if (event.allDay) {
    return start.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
  }
  const end = event.end ? new Date(event.end) : null
  const startStr = start.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  if (!end) return startStr
  const endStr = end.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  return `${startStr} – ${endStr}`
}

function priorityClass(priority) {
  if (priority === 'high') return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
  if (priority === 'medium') return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
  return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
}

// Linked tasks (todos)
const linkedTasks = ref([])
const tasksLoading = ref(false)
const taskDialogOpen = ref(false)
const editingTask = ref(null)
const addTaskEventId = ref(null)

const eventId = computed(() => props.event?.extendedProps?.raw?.id || null)

watch(
  () => props.modelValue,
  async (open) => {
    if (open && eventId.value) {
      await fetchLinkedTasks()
    } else if (!open) {
      taskDialogOpen.value = false
      editingTask.value = null
    }
  }
)

async function fetchLinkedTasks() {
  if (!eventId.value) return
  tasksLoading.value = true
  try {
    const { data } = await todosApi.list({ event_id: eventId.value })
    linkedTasks.value = data
  } catch (err) {
    console.error('Failed to fetch linked tasks', err)
  } finally {
    tasksLoading.value = false
  }
}

function openAddTask() {
  editingTask.value = null
  addTaskEventId.value = eventId.value
  taskDialogOpen.value = true
}

function openEditTask(task) {
  editingTask.value = { ...task }
  addTaskEventId.value = null
  taskDialogOpen.value = true
}

async function saveTask(taskData) {
  try {
    if (editingTask.value) {
      const { data } = await todosApi.update(editingTask.value.id, taskData)
      const idx = linkedTasks.value.findIndex((t) => t.id === data.id)
      if (idx !== -1) linkedTasks.value[idx] = data
    } else {
      const { data } = await todosApi.create({ ...taskData, event_id: taskData.event_id ?? eventId.value })
      linkedTasks.value.unshift(data)
    }
    emit('tasks-updated')
  } catch (err) {
    console.error('Failed to save task', err)
  }
  taskDialogOpen.value = false
  editingTask.value = null
}

async function toggleTask(task) {
  try {
    const { data } = await todosApi.update(task.id, { completed: !task.completed })
    const idx = linkedTasks.value.findIndex((t) => t.id === task.id)
    if (idx !== -1) linkedTasks.value[idx] = data
    emit('tasks-updated')
  } catch (err) {
    console.error('Failed to toggle task', err)
  }
}

async function removeTask(task) {
  try {
    await todosApi.delete(task.id)
    linkedTasks.value = linkedTasks.value.filter((t) => t.id !== task.id)
    emit('tasks-updated')
  } catch (err) {
    console.error('Failed to delete task', err)
  }
}

function close() {
  emit('update:modelValue', false)
}
</script>
