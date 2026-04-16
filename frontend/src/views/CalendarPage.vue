<template>
  <v-container fluid class="pa-4 pa-md-6">
    <div class="d-flex align-center mb-4">
      <div>
        <div class="text-h5 font-weight-bold">Calendar</div>
        <div class="text-body-2 text-medium-emphasis">Manage your schedule</div>
      </div>
      <v-spacer />
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        rounded="lg"
        elevation="0"
        @click="openAddEvent({ dateStr: new Date().toISOString(), allDay: false })"
      >
        New Event
      </v-btn>
    </div>

    <v-row>
      <!-- Calendar lists panel -->
      <v-col cols="12" md="3" lg="2">
        <v-card rounded="xl" elevation="0" border class="pa-3">
          <CalendarListPanel :calendar-lists="calendarLists" @update="fetchCalendarLists" />
        </v-card>
      </v-col>

      <!-- Calendar view -->
      <v-col cols="12" md="9" lg="10">
        <v-card rounded="xl" elevation="0" border>
          <v-card-text class="pa-4">
            <CalendarView
              :events="visibleCalendarEvents"
              @event-click="openEditEvent"
              @date-click="openAddEvent"
              @dates-set="fetchEventsForRange"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <EventDialog
      v-model="eventDialog.open"
      :event="eventDialog.event"
      :calendar-lists="calendarLists"
      @save="saveEvent"
      @delete="deleteEvent"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CalendarView from '../components/CalendarView.vue'
import EventDialog from '../components/EventDialog.vue'
import CalendarListPanel from '../components/CalendarListPanel.vue'
import { eventsApi, calendarListsApi } from '../api/index.js'

const events = ref([])
const calendarLists = ref([])

// Map of list id → list for quick lookup
const listMap = computed(() => {
  const map = {}
  for (const l of calendarLists.value) map[l.id] = l
  return map
})

// IDs of lists that are currently visible
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

// Filter out events from hidden lists
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
    const { data } = await eventsApi.list({
      start: start.toISOString(),
      end: end.toISOString(),
    })
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
