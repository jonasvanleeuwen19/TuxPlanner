<template>
  <div class="p-4 md:p-6">
    <div class="flex items-center mb-6">
      <div>
        <h1 class="text-xl font-bold">Tasks</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ pendingCount }} remaining</p>
      </div>
      <div class="flex-1" />
      <!-- Filter toggle -->
      <div class="flex rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden mr-3">
        <button
          v-for="opt in filterOptions"
          :key="opt.value"
          :class="[
            'px-3 py-1.5 text-xs font-medium transition-colors',
            filter === opt.value
              ? 'bg-blue-500 text-white'
              : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
          ]"
          @click="filter = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
      <button
        class="flex items-center gap-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
        @click="todoDialog = true"
      >
        <i class="mdi mdi-plus" />
        Add Task
      </button>
    </div>

    <div class="flex flex-col lg:flex-row gap-4">
      <!-- Todo lists sidebar -->
      <div class="lg:w-52 shrink-0">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-3 lg:sticky lg:top-[calc(3.5rem+1rem)]">
          <TodoListPanel
            :todo-lists="todoLists"
            :selected-list-id="selectedListId"
            :all-count="todos.filter((t) => !t.completed).length"
            @update="handleListUpdate"
            @select="selectList"
          />
        </div>
      </div>

      <!-- Tasks content -->
      <div class="flex-1 min-w-0">
        <!-- Loading bar -->
        <div v-if="loading" class="w-full h-1 bg-gray-200 dark:bg-gray-800 rounded mb-4 overflow-hidden">
          <div class="h-full bg-blue-500 animate-pulse w-full" />
        </div>

        <!-- Empty state -->
        <div v-if="filteredTodos.length === 0 && !loading" class="text-center py-16">
          <i class="mdi mdi-checkbox-marked-circle-outline text-6xl text-blue-300 dark:text-gray-600 block mb-4" />
          <h3 class="text-base font-medium text-gray-500 dark:text-gray-400">No tasks yet</h3>
          <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Create your first task to get started</p>
        </div>

        <!-- Category columns (horizontal scroll) -->
        <div v-else class="flex gap-4 overflow-x-auto pb-2" style="min-height: 200px;">
          <div
            v-for="category in categoryColumns"
            :key="category"
            class="flex-shrink-0 w-72"
          >
            <!-- Column header -->
            <div class="flex items-center mb-3 px-1">
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ category }}</span>
              <span class="ml-2 text-xs px-1.5 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                {{ getTodosForCategory(category).length }}
              </span>
            </div>
            <!-- Task cards in column -->
            <div class="flex flex-col gap-2">
              <div
                v-for="todo in getTodosForCategory(category)"
                :key="todo.id"
                :class="[
                  'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 transition-all hover:-translate-y-0.5 hover:shadow-md cursor-pointer',
                  todo.completed ? 'opacity-60' : ''
                ]"
                @click="openTodoInfo(todo)"
              >
                <div class="flex items-start gap-3">
                  <input
                    type="checkbox"
                    :checked="todo.completed"
                    class="mt-1 w-4 h-4 rounded accent-blue-500 cursor-pointer shrink-0"
                    @click.stop
                    @change="toggleTodo(todo)"
                  />
                  <div class="flex-1 min-w-0">
                    <p
                      :class="[
                        'text-sm font-medium',
                        todo.completed ? 'line-through text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-gray-100'
                      ]"
                    >
                      {{ todo.title }}
                    </p>
                    <div class="flex items-center gap-2 mt-2 flex-wrap">
                      <span
                        v-if="todo.priority"
                        :class="['text-xs px-2 py-0.5 rounded-md font-medium', priorityClass(todo.priority)]"
                      >
                        {{ todo.priority }}
                      </span>
                      <span
                        v-if="todo.due_date"
                        :class="[
                          'text-xs px-2 py-0.5 rounded-md font-medium flex items-center gap-1',
                          isOverdue(todo) ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                        ]"
                      >
                        <i class="mdi mdi-clock-outline text-xs" />
                        {{ formatDateTime(todo.due_date) }}
                      </span>
                      <span
                        v-if="todo.todo_list_id && selectedListId === null"
                        class="text-xs px-2 py-0.5 rounded-md font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                        :style="{ borderLeft: `3px solid ${getListColor(todo.todo_list_id)}` }"
                      >
                        {{ getListName(todo.todo_list_id) }}
                      </span>
                      <span
                        v-if="todo.event_id"
                        class="text-xs px-2 py-0.5 rounded-md font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 flex items-center gap-1"
                      >
                        <i class="mdi mdi-calendar-outline text-xs" />{{ getEventTitle(todo.event_id) }}
                      </span>
                    </div>
                  </div>
                  <button
                    class="shrink-0 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors"
                    @click.stop="deleteTodo(todo.id)"
                  >
                    <i class="mdi mdi-trash-can-outline text-base" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <TodoDialog
      v-model="todoDialog"
      :todo-lists="todoLists"
      :default-list-id="selectedListId"
      :existing-todos="todos"
      :events="events"
      @save="createTodo"
    />

    <!-- Edit Todo Dialog -->
    <TodoDialog
      v-model="editTodoDialog"
      :todo-lists="todoLists"
      :default-list-id="selectedListId"
      :existing-todos="todos"
      :edit-todo="editingTodo"
      :events="events"
      @save="updateTodo"
    />

    <!-- Todo Info Modal -->
    <Teleport to="body">
      <div
        v-if="infoModal.open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
        @click.self="infoModal.open = false"
      >
        <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
          <!-- Header -->
          <div class="flex items-center p-5 pb-3 shrink-0">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <input
                type="checkbox"
                :checked="infoModal.todo?.completed"
                class="w-4 h-4 accent-blue-500 cursor-pointer shrink-0"
                @change="toggleTodoFromModal"
              />
              <span
                :class="[
                  'text-base font-bold truncate',
                  infoModal.todo?.completed ? 'line-through text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-gray-100'
                ]"
              >{{ infoModal.todo?.title }}</span>
            </div>
            <div class="flex items-center gap-1 ml-2 shrink-0">
              <button
                class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
                @click="openEditTodo"
              >
                <i class="mdi mdi-pencil-outline" /> Edit
              </button>
              <button
                class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
                @click="infoModal.open = false"
              >
                <i class="mdi mdi-close text-lg" />
              </button>
            </div>
          </div>
          <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

          <!-- Body -->
          <div class="overflow-y-auto flex-1 p-5 space-y-4">
            <!-- Meta row -->
            <div class="flex flex-wrap gap-2">
              <span
                v-if="infoModal.todo?.priority"
                :class="['text-xs px-2 py-0.5 rounded-md font-medium', priorityClass(infoModal.todo.priority)]"
              >
                {{ infoModal.todo.priority }}
              </span>
              <span
                v-if="infoModal.todo?.category"
                class="text-xs px-2 py-0.5 rounded-md font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
              >
                <i class="mdi mdi-folder-outline text-xs mr-1" />{{ infoModal.todo.category }}
              </span>
              <span
                v-if="infoModal.todo?.due_date"
                :class="[
                  'text-xs px-2 py-0.5 rounded-md font-medium flex items-center gap-1',
                  isOverdue(infoModal.todo) ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                ]"
              >
                <i class="mdi mdi-clock-outline text-xs" />
                Due {{ formatDateTime(infoModal.todo.due_date) }}
              </span>
            </div>

            <!-- Created date -->
            <div v-if="infoModal.todo?.created_at" class="flex items-center gap-2">
              <i class="mdi mdi-calendar-plus-outline text-sm text-gray-400 dark:text-gray-500" />
              <span class="text-xs text-gray-500 dark:text-gray-400">Created {{ formatDateTime(infoModal.todo.created_at) }}</span>
            </div>

            <!-- Linked event -->
            <div v-if="infoModal.todo?.event_id" class="flex items-center gap-2">
              <i class="mdi mdi-calendar-link text-sm text-gray-400 dark:text-gray-500" />
              <span class="text-xs px-2 py-0.5 rounded-md font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                <i class="mdi mdi-calendar-outline text-xs mr-1" />{{ getEventTitle(infoModal.todo.event_id) }}
              </span>
            </div>

            <!-- List -->
            <div v-if="infoModal.todo?.todo_list_id" class="flex items-center gap-2">
              <i class="mdi mdi-view-list text-sm text-gray-400 dark:text-gray-500" />
              <span
                class="text-xs px-2 py-0.5 rounded-md font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                :style="{ borderLeft: `3px solid ${getListColor(infoModal.todo.todo_list_id)}` }"
              >
                {{ getListName(infoModal.todo.todo_list_id) }}
              </span>
            </div>

            <!-- Description (rendered markdown) -->
            <div v-if="infoModal.todo?.description">
              <div class="flex items-start gap-2">
                <i class="mdi mdi-text-box-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" />
                <div
                  class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm max-w-none dark:prose-invert flex-1"
                  v-html="renderedTodoDescription"
                />
              </div>
            </div>
          </div>

          <!-- Footer -->
          <hr class="border-gray-200 dark:border-gray-700 shrink-0" />
          <div class="flex items-center gap-2 p-4 shrink-0">
            <button
              :class="[
                'flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
                infoModal.todo?.completed
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                  : 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40'
              ]"
              @click="toggleTodoFromModal"
            >
              <i :class="['mdi', infoModal.todo?.completed ? 'mdi-undo' : 'mdi-check']" />
              {{ infoModal.todo?.completed ? 'Mark Incomplete' : 'Complete' }}
            </button>
            <div class="flex-1" />
            <button
              class="flex items-center gap-1 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              @click="deleteTodoFromModal"
            >
              <i class="mdi mdi-trash-can" /> Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import TodoDialog from '../components/TodoDialog.vue'
import TodoListPanel from '../components/TodoListPanel.vue'
import { todosApi, todoListsApi, eventsApi } from '../api/index.js'

const todos = ref([])
const todoLists = ref([])
const events = ref([])
const loading = ref(false)
const todoDialog = ref(false)
const editTodoDialog = ref(false)
const editingTodo = ref(null)
const filter = ref('all')
const selectedListId = ref(null)

const infoModal = ref({ open: false, todo: null })

const filterOptions = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Active' },
  { value: 'completed', label: 'Done' },
]

const listMap = computed(() => {
  const m = {}
  for (const l of todoLists.value) m[l.id] = l
  return m
})

function getListColor(id) { return listMap.value[id]?.color || '#3b82f6' }
function getListName(id) { return listMap.value[id]?.name || '' }
function getEventTitle(id) { return events.value.find((e) => e.id === id)?.title || `Event #${id}` }

const filteredByList = computed(() =>
  selectedListId.value === null
    ? todos.value
    : todos.value.filter((t) => t.todo_list_id === selectedListId.value)
)

const filteredTodos = computed(() => {
  if (filter.value === 'pending') return filteredByList.value.filter((t) => !t.completed)
  if (filter.value === 'completed') return filteredByList.value.filter((t) => t.completed)
  return filteredByList.value
})

// Unique sorted categories from filtered todos
const categoryColumns = computed(() => {
  const cats = new Set()
  for (const t of filteredTodos.value) {
    cats.add(t.category || 'Default')
  }
  const sorted = [...cats].sort((a, b) => {
    if (a === 'Default') return -1
    if (b === 'Default') return 1
    return a.localeCompare(b)
  })
  return sorted
})

function getTodosForCategory(category) {
  return filteredTodos.value.filter((t) => (t.category || 'Default') === category)
}

const pendingCount = computed(() => filteredByList.value.filter((t) => !t.completed).length)

const renderedTodoDescription = computed(() => {
  if (!infoModal.value.todo?.description) return ''
  return DOMPurify.sanitize(marked.parse(infoModal.value.todo.description))
})

async function fetchTodos() {
  loading.value = true
  try {
    const { data } = await todosApi.list()
    todos.value = data
  } catch (err) {
    console.error('Failed to fetch todos', err)
  } finally {
    loading.value = false
  }
}

async function fetchTodoLists() {
  try {
    const { data } = await todoListsApi.list()
    todoLists.value = data
  } catch (err) {
    console.error('Failed to fetch todo lists', err)
  }
}

async function createTodo(todoData) {
  try {
    const { data } = await todosApi.create({
      ...todoData,
      todo_list_id: todoData.todo_list_id ?? (selectedListId.value ?? null),
    })
    todos.value.unshift(data)
  } catch (err) {
    console.error('Failed to create todo', err)
  }
  todoDialog.value = false
}

async function updateTodo(todoData) {
  if (!editingTodo.value) return
  try {
    const { data } = await todosApi.update(editingTodo.value.id, todoData)
    const idx = todos.value.findIndex((t) => t.id === data.id)
    if (idx !== -1) todos.value[idx] = data
    // Update info modal if it's showing this task
    if (infoModal.value.todo?.id === data.id) {
      infoModal.value.todo = data
    }
  } catch (err) {
    console.error('Failed to update todo', err)
  }
  editTodoDialog.value = false
  editingTodo.value = null
}

async function toggleTodo(todo) {
  try {
    const { data } = await todosApi.update(todo.id, { completed: !todo.completed })
    const idx = todos.value.findIndex((t) => t.id === data.id)
    if (idx !== -1) todos.value[idx] = data
  } catch (err) {
    console.error('Failed to toggle todo', err)
  }
}

async function toggleTodoFromModal() {
  if (!infoModal.value.todo) return
  await toggleTodo(infoModal.value.todo)
  // Update modal reference
  const updated = todos.value.find((t) => t.id === infoModal.value.todo.id)
  if (updated) infoModal.value.todo = updated
}

async function deleteTodo(id) {
  try {
    await todosApi.delete(id)
    todos.value = todos.value.filter((t) => t.id !== id)
  } catch (err) {
    console.error('Failed to delete todo', err)
  }
}

async function deleteTodoFromModal() {
  if (!infoModal.value.todo) return
  await deleteTodo(infoModal.value.todo.id)
  infoModal.value.open = false
}

function openTodoInfo(todo) {
  infoModal.value = { open: true, todo }
}

function openEditTodo() {
  editingTodo.value = { ...infoModal.value.todo }
  infoModal.value.open = false
  editTodoDialog.value = true
}

function selectList(id) {
  selectedListId.value = id
}

async function handleListUpdate(payload) {
  await fetchTodoLists()
  if (payload?.deletedId && selectedListId.value === payload.deletedId) {
    selectedListId.value = null
  }
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function isOverdue(todo) {
  return !todo.completed && todo.due_date && new Date(todo.due_date) < new Date()
}

function priorityClass(priority) {
  if (priority === 'high') return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
  if (priority === 'medium') return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
  return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
}

onMounted(async () => {
  await fetchTodoLists()
  await fetchTodos()
  try {
    // Fetch upcoming events for task-event linking (past 30 days to 1 year ahead)
    const start = new Date()
    start.setDate(start.getDate() - 30)
    const end = new Date()
    end.setFullYear(end.getFullYear() + 1)
    const { data } = await eventsApi.list({ start: start.toISOString(), end: end.toISOString() })
    events.value = data
  } catch (err) {
    console.error('Failed to fetch events', err)
  }
})
</script>
