<template>
  <v-container fluid class="pa-4 pa-md-6">
    <div class="d-flex align-center mb-6">
      <div>
        <div class="text-h5 font-weight-bold">Tasks</div>
        <div class="text-body-2 text-medium-emphasis">{{ pendingCount }} remaining</div>
      </div>
      <v-spacer />
      <v-btn-toggle v-model="filter" mandatory density="compact" rounded="lg" color="primary" class="mr-3">
        <v-btn value="all" size="small">All</v-btn>
        <v-btn value="pending" size="small">Active</v-btn>
        <v-btn value="completed" size="small">Done</v-btn>
      </v-btn-toggle>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        rounded="lg"
        elevation="0"
        @click="todoDialog = true"
      >
        Add Task
      </v-btn>
    </div>

    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" rounded />

    <div v-if="filteredTodos.length === 0 && !loading" class="text-center py-16">
      <v-icon icon="mdi-checkbox-marked-circle-outline" size="64" color="primary" opacity="0.3" class="mb-4" />
      <div class="text-h6 text-medium-emphasis font-weight-medium">No tasks yet</div>
      <div class="text-body-2 text-disabled mt-1">Create your first task to get started</div>
    </div>

    <v-row>
      <v-col
        v-for="todo in filteredTodos"
        :key="todo.id"
        cols="12"
        sm="6"
        lg="4"
      >
        <v-card
          rounded="xl"
          elevation="0"
          border
          :class="{ 'todo-completed': todo.completed }"
          class="todo-card"
        >
          <v-card-text class="pa-4">
            <div class="d-flex align-start gap-3">
              <v-checkbox-btn
                :model-value="todo.completed"
                color="primary"
                class="mt-1 flex-shrink-0"
                @update:model-value="toggleTodo(todo)"
              />
              <div class="flex-grow-1 min-width-0">
                <div
                  class="text-body-1 font-weight-medium"
                  :class="{ 'text-decoration-line-through text-disabled': todo.completed }"
                >
                  {{ todo.title }}
                </div>
                <div v-if="todo.description" class="text-body-2 text-medium-emphasis mt-1 text-truncate">
                  {{ todo.description }}
                </div>
                <div class="d-flex align-center gap-2 mt-2 flex-wrap">
                  <v-chip
                    v-if="todo.priority"
                    size="x-small"
                    :color="priorityColor(todo.priority)"
                    variant="tonal"
                    rounded="lg"
                  >
                    {{ todo.priority }}
                  </v-chip>
                  <v-chip
                    v-if="todo.due_date"
                    size="x-small"
                    :color="isOverdue(todo) ? 'error' : 'default'"
                    variant="tonal"
                    prepend-icon="mdi-clock-outline"
                    rounded="lg"
                  >
                    {{ formatDateTime(todo.due_date) }}
                  </v-chip>
                </div>
              </div>
              <v-btn
                icon="mdi-trash-can-outline"
                size="x-small"
                variant="text"
                color="error"
                class="flex-shrink-0"
                @click="deleteTodo(todo.id)"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <TodoDialog v-model="todoDialog" @save="createTodo" />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TodoDialog from '../components/TodoDialog.vue'
import { todosApi } from '../api/index.js'

const todos = ref([])
const loading = ref(false)
const todoDialog = ref(false)
const filter = ref('all')

const filteredTodos = computed(() => {
  if (filter.value === 'pending') return todos.value.filter((t) => !t.completed)
  if (filter.value === 'completed') return todos.value.filter((t) => t.completed)
  return todos.value
})

const pendingCount = computed(() => todos.value.filter((t) => !t.completed).length)

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

async function createTodo(todoData) {
  try {
    const { data } = await todosApi.create(todoData)
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

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function isOverdue(todo) {
  return !todo.completed && todo.due_date && new Date(todo.due_date) < new Date()
}

function priorityColor(priority) {
  if (priority === 'high') return 'error'
  if (priority === 'medium') return 'warning'
  return 'success'
}

onMounted(fetchTodos)
</script>

<style scoped>
.todo-card {
  transition: box-shadow 0.2s, transform 0.2s;
}

.todo-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
  transform: translateY(-1px);
}

.todo-completed {
  opacity: 0.65;
}

.min-width-0 {
  min-width: 0;
}
</style>
