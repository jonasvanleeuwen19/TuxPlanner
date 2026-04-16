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
          />
        </div>
      </div>

      <!-- Calendar view -->
      <div class="flex-1 min-w-0">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4">
          <CalendarView
            :events="visibleCalendarEvents"
            @event-click="openEditEvent"
            @date-click="openAddEvent"
            @dates-set="fetchEventsForRange"
          />
        </div>
      </div>
    </div>

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
import CalendarListPanel from '../components/CalendarListPanel.vue'
import { eventsApi, calendarListsApi, todosApi } from '../api/index.js'

const TODO_LIST_ID = 'todos-virtual'
const TODO_LIST_COLOR = '#f59e0b'

const events = ref([])
const calendarLists = ref([])
const todos = ref([])

const todoListVisible = ref(
  localStorage.getItem('todoListVisible') !== 'false'
)

// The virtual "TODO's" list entry for the panel
const todoVirtualList = {
  id: TODO_LIST_ID,
  name: "TODO's",
  color: TODO_LIST_COLOR,
  ical_feed_id: null,
  is_virtual: true,
}

// For the panel, include the virtual TODO's list
const calendarListsForPanel = computed(() => [
  ...calendarLists.value,
  { ...todoVirtualList, is_visible: todoListVisible.value },
])

const listMap = computed(() => {
  const map = {}
  for (const l of calendarLists.value) map[l.id] = l
  return map
})

const visibleListIds = computed(() => new Set(
  calendarLists.value.filter((l) => l.is_visible).map((l) => l.id)
))

// Events from DB with subtask_category_names
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
        subtask_category_names: e.subtask_category_names || [],
      },
    }
  })
)

// Virtual todo events (todos with due_date)
const todoEvents = computed(() =>
  todos.value
    .filter((t) => t.due_date)
    .map((t) => ({
      id: `todo-${t.id}`,
      title: `✓ ${t.title}`,
      start: t.due_date,
      end: t.due_date,
      allDay: false,
      backgroundColor: TODO_LIST_COLOR,
      calendar_list_id: TODO_LIST_ID,
      extendedProps: {
        description: t.description,
        location: null,
        source: 'todo',
        raw: t,
        subtask_category_names: [],
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

async function fetchEventsForRange({ start, end }) {
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

const eventDialog = ref({ open: false, event: null })

function openAddEvent({ dateStr, allDay }) {
  eventDialog.value = {
    open: true,
    event: { title: '', start: dateStr, end: null, all_day: allDay, color: null, description: '', location: '', calendar_list_id: null },
  }
}

function openEditEvent({ event }) {
  // Don't open edit for virtual TODO events
  if (event.extendedProps?.source === 'todo') return
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

function handleToggleVirtual() {
  todoListVisible.value = !todoListVisible.value
  localStorage.setItem('todoListVisible', String(todoListVisible.value))
}

onMounted(async () => {
  await fetchCalendarLists()
  try {
    const { data } = await todosApi.list()
    todos.value = data
  } catch (err) {
    console.error('Failed to fetch todos', err)
  }
})
</script>
