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
      <!-- Calendar lists panel -->
      <div class="lg:w-52 shrink-0">
        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-3">
          <CalendarListPanel :calendar-lists="calendarLists" @update="fetchCalendarLists" />
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
import { eventsApi, calendarListsApi } from '../api/index.js'

const events = ref([])
const calendarLists = ref([])

const listMap = computed(() => {
  const map = {}
  for (const l of calendarLists.value) map[l.id] = l
  return map
})

const visibleListIds = computed(() => new Set(
  calendarLists.value.filter((l) => l.is_visible).map((l) => l.id)
))

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
      extendedProps: { description: e.description, location: e.location, source: e.source, raw: e },
    }
  })
)

const visibleCalendarEvents = computed(() =>
  calendarEvents.value.filter((e) => {
    if (e.calendar_list_id === null || e.calendar_list_id === undefined) return true
    return visibleListIds.value.has(e.calendar_list_id)
  })
)

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
}

const eventDialog = ref({ open: false, event: null })

function openAddEvent({ dateStr, allDay }) {
  eventDialog.value = {
    open: true,
    event: { title: '', start: dateStr, end: null, all_day: allDay, color: null, description: '', location: '', calendar_list_id: null },
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

onMounted(fetchCalendarLists)
</script>
