<template>
  <div class="p-4 md:p-6">
    <div class="flex items-center mb-4">
      <div>
        <h1 class="text-xl font-bold">Calendar</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">Manage your schedule</p>
      </div>
      <div class="flex-1" />
      <button
        class="flex items-center gap-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
        @click="openAddEvent({ dateStr: new Date().toISOString(), allDay: false })"
      >
        <i class="mdi mdi-plus" />
        New Event
      </button>
    </div>

    <div class="flex flex-col lg:flex-row gap-4">
      <!-- Calendar lists panel — sticky -->
      <div class="lg:w-52 shrink-0">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-3 lg:sticky lg:top-[calc(3.5rem+1rem)]">
          <CalendarListPanel
            :calendar-lists="calendarListsForPanel"
            @update="fetchCalendarLists"
            @toggle-virtual="handleToggleVirtual"
            @edit-virtual="handleEditVirtual"
          />
        </div>
      </div>

      <!-- Calendar view -->
      <div class="flex-1 min-w-0">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4">
          <CalendarView
            :events="visibleCalendarEvents"
            @event-click="openEventInfo"
            @date-click="openAddEvent"
            @dates-set="fetchEventsForRange"
          />
        </div>
      </div>
    </div>

    <!-- Event Info Modal (shown on event click) -->
    <EventInfoModal
      v-model="infoModal.open"
      :event="infoModal.event"
      :events="events"
      :todo-lists="todoLists"
      @edit="openEditFromInfo"
      @tasks-updated="handleTasksUpdated"
    />

    <!-- Event Edit/Create Dialog -->
    <EventDialog
      v-model="eventDialog.open"
      :event="eventDialog.event"
      :calendar-lists="calendarLists"
      @save="saveEvent"
      @delete="deleteEvent"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CalendarView from '../components/CalendarView.vue'
import EventDialog from '../components/EventDialog.vue'
import EventInfoModal from '../components/EventInfoModal.vue'
import CalendarListPanel from '../components/CalendarListPanel.vue'
import { eventsApi, calendarListsApi, todosApi, todoListsApi } from '../api/index.js'

const TODO_LIST_ID = 'todos-virtual'
const DEFAULT_TODO_COLOR = '#f59e0b'

const events = ref([])
const calendarLists = ref([])
const todos = ref([])
const todoLists = ref([])
const currentRange = ref(null)

const todoListVisible = ref(
  localStorage.getItem('todoListVisible') !== 'false'
)

const todoListColor = ref(
  localStorage.getItem('todoListColor') || DEFAULT_TODO_COLOR
)

// The virtual "TODO's" list entry for the panel
const todoVirtualList = computed(() => ({
  id: TODO_LIST_ID,
  name: "TODO's",
  color: todoListColor.value,
  ical_feed_id: null,
  is_virtual: true,
}))

// For the panel, include the virtual TODO's list
const calendarListsForPanel = computed(() => [
  ...calendarLists.value,
  { ...todoVirtualList.value, is_visible: todoListVisible.value },
])

const listMap = computed(() => {
  const map = {}
  for (const l of calendarLists.value) map[l.id] = l
  return map
})

const visibleListIds = computed(() => new Set(
  calendarLists.value.filter((l) => l.is_visible).map((l) => l.id)
))

// Events from DB with task_count
const calendarEvents = computed(() =>
  events.value.map((e) => {
    const list = e.calendar_list_id ? listMap.value[e.calendar_list_id] : null
    const color = list ? list.color : (e.color || '#3b82f6')
    return {
      id: String(e.id),
      title: e.title,
      start: e.start,
      end: e.end,
      allDay: e.all_day,
      backgroundColor: color,
      calendar_list_id: e.calendar_list_id,
      extendedProps: {
        description: e.description,
        location: e.location,
        source: e.source,
        raw: e,
        task_count: e.task_count || 0,
      },
    }
  })
)

// Virtual todo events: only todos with due_date and NOT linked to an event
const todoEvents = computed(() =>
  todos.value
    .filter((t) => t.due_date && !t.event_id)
    .map((t) => ({
      id: `todo-${t.id}`,
      title: `✓ ${t.title}`,
      start: t.due_date,
      end: t.due_date,
      allDay: true,
      backgroundColor: todoListColor.value,
      calendar_list_id: TODO_LIST_ID,
      extendedProps: {
        description: t.description,
        location: null,
        source: 'todo',
        raw: t,
        task_count: 0,
      },
    }))
)

const visibleCalendarEvents = computed(() => {
  const regularEvents = calendarEvents.value.filter((e) => {
    if (e.calendar_list_id === null || e.calendar_list_id === undefined) return true
    return visibleListIds.value.has(e.calendar_list_id)
  })
  const todoEventsFiltered = todoListVisible.value ? todoEvents.value : []
  return [...regularEvents, ...todoEventsFiltered]
})

async function fetchCalendarLists() {
  try {
    const { data } = await calendarListsApi.list()
    calendarLists.value = data
  } catch (err) {
    console.error('Failed to fetch calendar lists', err)
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

async function fetchEventsForRange({ start, end }) {
  currentRange.value = { start, end }
  try {
    const { data } = await eventsApi.list({ start: start.toISOString(), end: end.toISOString() })
    events.value = data
  } catch (err) {
    console.error('Failed to fetch events', err)
  }
  // Also refresh todos
  try {
    const { data } = await todosApi.list()
    todos.value = data
  } catch (err) {
    console.error('Failed to fetch todos', err)
  }
}

// Info modal state
const infoModal = ref({ open: false, event: null })
// Edit dialog state
const eventDialog = ref({ open: false, event: null })

function openAddEvent({ dateStr, allDay }) {
  // Always open with all_day=false so time & end fields are visible
  const startStr = allDay
    ? new Date(dateStr).toISOString().slice(0, 10) + 'T09:00'
    : new Date(dateStr).toISOString().slice(0, 16)
  eventDialog.value = {
    open: true,
    event: { title: '', start: startStr, end: null, all_day: false, color: null, description: '', location: '', calendar_list_id: null },
  }
}

function openEventInfo({ event }) {
  // Don't open info for virtual TODO events
  if (event.extendedProps?.source === 'todo') return
  infoModal.value = { open: true, event }
}

function openEditFromInfo() {
  if (!infoModal.value.event) return
  const raw = infoModal.value.event.extendedProps.raw
  infoModal.value.open = false
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

function handleToggleVirtual() {
  todoListVisible.value = !todoListVisible.value
  localStorage.setItem('todoListVisible', String(todoListVisible.value))
}

function handleEditVirtual(newColor) {
  todoListColor.value = newColor
  localStorage.setItem('todoListColor', newColor)
}

async function handleTasksUpdated() {
  // Refresh events to update task_count, and refresh todos
  if (currentRange.value) {
    await fetchEventsForRange(currentRange.value)
  }
}

onMounted(async () => {
  await Promise.all([fetchCalendarLists(), fetchTodoLists()])
  try {
    const { data } = await todosApi.list()
    todos.value = data
  } catch (err) {
    console.error('Failed to fetch todos', err)
  }
})
</script>
