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

    <v-card rounded="xl" elevation="0" border>
      <v-card-text class="pa-4">
        <CalendarView
          :events="calendarEvents"
          :is-dark="isDark"
          @event-click="openEditEvent"
          @date-click="openAddEvent"
          @select="openFromSelect"
          @event-drop="handleEventDrop"
          @dates-set="fetchEventsForRange"
        />
      </v-card-text>
    </v-card>

    <EventDialog
      v-model="eventDialog.open"
      :event="eventDialog.event"
      @save="saveEvent"
      @delete="deleteEvent"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import CalendarView from '../components/CalendarView.vue'
import EventDialog from '../components/EventDialog.vue'
import { eventsApi } from '../api/index.js'
import { useTheme } from 'vuetify'

const theme = useTheme()
const isDark = computed(() => theme.global.name.value === 'dark')

const events = ref([])

const calendarEvents = computed(() =>
  events.value.map((e) => ({
    id: String(e.id),
    title: e.title,
    start: e.start,
    end: e.end,
    allDay: e.all_day,
    backgroundColor: e.color || '#6366f1',
    borderColor: 'transparent',
    extendedProps: { description: e.description, location: e.location, source: e.source, raw: e },
  }))
)

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
    event: { title: '', start: dateStr, end: null, all_day: allDay, color: null, description: '', location: '' },
  }
}

function openFromSelect({ startStr, endStr, allDay }) {
  eventDialog.value = {
    open: true,
    event: { title: '', start: startStr, end: endStr, all_day: allDay, color: null, description: '', location: '' },
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
</script>
