<template>
  <v-app :theme="theme">
    <!-- Top App Bar -->
    <v-app-bar color="primary" density="compact" elevation="2">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title>
        <v-icon icon="mdi-penguin" class="mr-2" />
        TuxPlanner
      </v-app-bar-title>
      <v-spacer />
      <v-btn :icon="theme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night'" @click="toggleTheme" />
    </v-app-bar>

    <!-- Sidebar Navigation Drawer -->
    <v-navigation-drawer v-model="drawer" :width="300" color="surface">
      <Sidebar
        :todos="todos"
        :loading-todos="loadingTodos"
        @add-todo="openAddTodo"
        @toggle-todo="toggleTodo"
        @delete-todo="deleteTodo"
      />
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="bg-background">
      <v-container fluid class="pa-4">
        <CalendarView
          :events="calendarEvents"
          @event-click="openEditEvent"
          @date-click="openAddEvent"
          @event-drop="handleEventDrop"
          @dates-set="fetchEventsForRange"
        />
      </v-container>
    </v-main>

    <!-- Add/Edit Event Dialog -->
    <EventDialog
      v-model="eventDialog.open"
      :event="eventDialog.event"
      @save="saveEvent"
      @delete="deleteEvent"
    />

    <!-- Add Todo Dialog -->
    <TodoDialog
      v-model="todoDialog"
      @save="createTodo"
    />
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CalendarView from './components/CalendarView.vue'
import Sidebar from './components/Sidebar.vue'
import EventDialog from './components/EventDialog.vue'
import TodoDialog from './components/TodoDialog.vue'
import { eventsApi, todosApi } from './api/index.js'

// ── Theme ─────────────────────────────────────────────────────────────────────
const theme = ref('light')
function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

// ── Drawer ────────────────────────────────────────────────────────────────────
const drawer = ref(true)

// ── Events ────────────────────────────────────────────────────────────────────
const events = ref([])
const loadingEvents = ref(false)

const calendarEvents = computed(() =>
  events.value.map((e) => ({
    id: String(e.id),
    title: e.title,
    start: e.start,
    end: e.end,
    allDay: e.all_day,
    backgroundColor: e.color || '#1565C0',
    borderColor: e.color || '#1565C0',
    extendedProps: { description: e.description, raw: e },
  }))
)

async function fetchEventsForRange({ start, end }) {
  loadingEvents.value = true
  try {
    const { data } = await eventsApi.list({
      start: start.toISOString(),
      end: end.toISOString(),
    })
    events.value = data
  } catch (err) {
    console.error('Failed to fetch events', err)
  } finally {
    loadingEvents.value = false
  }
}

// ── Event Dialog ─────────────────────────────────────────────────────────────
const eventDialog = ref({ open: false, event: null })

function openAddEvent({ dateStr, allDay }) {
  eventDialog.value = {
    open: true,
    event: { title: '', start: dateStr, end: null, all_day: allDay, color: null, description: '' },
  }
}

function openEditEvent({ event }) {
  const raw = event.extendedProps.raw
  eventDialog.value = { open: true, event: { ...raw } }
}

async function saveEvent(eventData) {
  try {
    if (eventData.id) {
      const { data } = await eventsApi.update(eventData.id, eventData)
      const idx = events.value.findIndex((e) => e.id === data.id)
      if (idx !== -1) events.value[idx] = data
    } else {
      const { data } = await eventsApi.create(eventData)
      events.value.push(data)
    }
  } catch (err) {
    console.error('Failed to save event', err)
  }
  eventDialog.value.open = false
}

async function deleteEvent(id) {
  try {
    await eventsApi.delete(id)
    events.value = events.value.filter((e) => e.id !== id)
  } catch (err) {
    console.error('Failed to delete event', err)
  }
  eventDialog.value.open = false
}

async function handleEventDrop({ event }) {
  const raw = event.extendedProps.raw
  try {
    const { data } = await eventsApi.update(raw.id, {
      ...raw,
      start: event.start.toISOString(),
      end: event.end ? event.end.toISOString() : null,
    })
    const idx = events.value.findIndex((e) => e.id === data.id)
    if (idx !== -1) events.value[idx] = data
  } catch (err) {
    console.error('Failed to update event after drop', err)
  }
}

// ── Todos ─────────────────────────────────────────────────────────────────────
const todos = ref([])
const loadingTodos = ref(false)
const todoDialog = ref(false)

async function fetchTodos() {
  loadingTodos.value = true
  try {
    const { data } = await todosApi.list()
    todos.value = data
  } catch (err) {
    console.error('Failed to fetch todos', err)
  } finally {
    loadingTodos.value = false
  }
}

function openAddTodo() {
  todoDialog.value = true
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

onMounted(() => {
  fetchTodos()
})
</script>
