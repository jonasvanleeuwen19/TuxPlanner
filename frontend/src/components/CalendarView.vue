<template>
  <div class="calendar-wrapper">
    <FullCalendar :options="calendarOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'

const props = defineProps({
  events: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['event-click', 'date-click', 'event-drop', 'dates-set'])

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  events: props.events,
  editable: true,
  selectable: true,
  dayMaxEvents: true,
  weekends: true,
  height: 'auto',
  locale: 'nl',
  buttonText: {
    today: 'Vandaag',
    month: 'Maand',
    week: 'Week',
    day: 'Dag',
  },
  eventClick: (info) => emit('event-click', info),
  dateClick: (info) => emit('date-click', info),
  eventDrop: (info) => emit('event-drop', info),
  datesSet: (info) => emit('dates-set', info),
}))
</script>

<style scoped>
.calendar-wrapper {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

:deep(.fc-button-primary) {
  background-color: #1565c0 !important;
  border-color: #1565c0 !important;
}

:deep(.fc-button-primary:hover) {
  background-color: #0d47a1 !important;
  border-color: #0d47a1 !important;
}

:deep(.fc-button-active) {
  background-color: #0d47a1 !important;
  border-color: #0d47a1 !important;
}

:deep(.fc-event) {
  cursor: pointer;
  border-radius: 4px;
}

:deep(.fc-daygrid-event) {
  font-size: 0.85em;
}
</style>
