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

        <!-- Tasks grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="todo in filteredTodos"
            :key="todo.id"
            :class="[
              'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 transition-all hover:-translate-y-0.5 hover:shadow-md',
              todo.completed ? 'opacity-60' : ''
            ]"
          >
            <div class="flex items-start gap-3">
              <input
                type="checkbox"
                :checked="todo.completed"
                class="mt-1 w-4 h-4 rounded accent-blue-500 cursor-pointer shrink-0"
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
                <p v-if="todo.description" class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
                  {{ todo.description }}
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
                </div>
              </div>
              <button
                class="shrink-0 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors"
                @click="deleteTodo(todo.id)"
              >
                <i class="mdi mdi-trash-can-outline text-base" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <TodoDialog
      v-model="todoDialog"
      :todo-lists="todoLists"
      :default-list-id="selectedListId"
      @save="createTodo"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TodoDialog from '../components/TodoDialog.vue'
import TodoListPanel from '../components/TodoListPanel.vue'
import { todosApi, todoListsApi } from '../api/index.js'

const todos = ref([])
const todoLists = ref([])
const loading = ref(false)
const todoDialog = ref(false)
const filter = ref('all')
const selectedListId = ref(null)

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

const pendingCount = computed(() => filteredByList.value.filter((t) => !t.completed).length)

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

async function toggleTodo(todo) {
  try {
    const { data } = await todosApi.update(todo.id, { completed: !todo.completed })
    const idx = todos.value.findIndex((t) => t.id === data.id)
    if (idx !== -1) todos.value[idx] = data
  } catch (err) {
    console.error('Failed to toggle todo', err)
  }
}

async function deleteTodo(id) {
  try {
    await todosApi.delete(id)
    todos.value = todos.value.filter((t) => t.id !== id)
  } catch (err) {
    console.error('Failed to delete todo', err)
  }
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
})
</script>
