<template>
  <div class="calendar-wrapper" :class="{ 'calendar-dark': isDark }">
    <FullCalendar ref="calendarRef" :options="calendarOptions" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'

const props = defineProps({
  events: {
    type: Array,
    default: () => [],
  },
  isDark: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['event-click', 'date-click', 'event-drop', 'dates-set', 'select'])

const calendarRef = ref(null)

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
  },
  buttonText: {
    today: 'Today',
    month: 'Month',
    week: 'Week',
    day: 'Day',
    list: 'List',
  },
  events: props.events,
  editable: true,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: 3,
  weekends: true,
  height: 'auto',
  locale: 'en',
  nowIndicator: true,
  weekNumbers: true,
  weekNumberFormat: { week: 'short' },
  eventTimeFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
  slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
  eventContent: renderEventContent,
  eventClick: (info) => emit('event-click', info),
  dateClick: (info) => emit('date-click', info),
  eventDrop: (info) => emit('event-drop', info),
  datesSet: (info) => emit('dates-set', info),
  select: (info) => emit('select', info),
}))

function renderEventContent(arg) {
  const isIcal = arg.event.extendedProps?.source === 'ical'
  const location = arg.event.extendedProps?.location
  return {
    html: `<div class="fc-event-inner">
      <span class="fc-event-title-text">${arg.event.title}</span>
      ${location ? `<span class="fc-event-location"><span class="mdi mdi-map-marker-outline"></span>${location}</span>` : ''}
      ${isIcal ? '<span class="fc-event-ical-badge">iCal</span>' : ''}
    </div>`,
  }
}
</script>

<style scoped>
.calendar-wrapper {
  background: transparent;
  border-radius: 20px;
  overflow: hidden;
}

:deep(.fc) {
  font-family: 'Inter', 'Roboto', sans-serif;
}

:deep(.fc-toolbar-title) {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.3px;
}

:deep(.fc-button-primary) {
  background-color: #6366f1 !important;
  border-color: #6366f1 !important;
  border-radius: 8px !important;
  font-weight: 500;
  font-size: 0.8rem;
  text-transform: none;
  box-shadow: none !important;
  padding: 4px 12px;
}

:deep(.fc-button-primary:hover) {
  background-color: #4f46e5 !important;
  border-color: #4f46e5 !important;
}

:deep(.fc-button-active) {
  background-color: #4338ca !important;
  border-color: #4338ca !important;
}

:deep(.fc-button-group) {
  gap: 2px;
}

:deep(.fc-daygrid-day-number) {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 6px 8px;
}

:deep(.fc-col-header-cell-cushion) {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 0;
}

:deep(.fc-daygrid-day.fc-day-today) {
  background: rgba(99, 102, 241, 0.08) !important;
}

:deep(.fc-daygrid-day.fc-day-today .fc-daygrid-day-number) {
  background: #6366f1;
  color: white;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 4px;
}

:deep(.fc-event) {
  border: none !important;
  border-radius: 6px !important;
  padding: 1px 4px;
  cursor: pointer;
  margin-bottom: 1px;
}

:deep(.fc-event-inner) {
  display: flex;
  flex-direction: column;
  gap: 1px;
  overflow: hidden;
}

:deep(.fc-event-title-text) {
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.fc-event-location) {
  font-size: 0.7rem;
  opacity: 0.85;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.fc-event-ical-badge) {
  font-size: 0.6rem;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 3px;
  padding: 0 3px;
  align-self: flex-start;
}

:deep(.fc-list-event) {
  cursor: pointer;
}

:deep(.fc-list-event:hover td) {
  background: rgba(99, 102, 241, 0.06);
}

:deep(.fc-highlight) {
  background: rgba(99, 102, 241, 0.15) !important;
  border-radius: 4px;
}

:deep(.fc-timegrid-now-indicator-line) {
  border-color: #6366f1;
}

:deep(.fc-timegrid-now-indicator-arrow) {
  border-top-color: #6366f1;
  border-bottom-color: #6366f1;
}

.calendar-dark :deep(.fc-theme-standard td),
.calendar-dark :deep(.fc-theme-standard th),
.calendar-dark :deep(.fc-theme-standard .fc-scrollgrid) {
  border-color: rgba(255, 255, 255, 0.08) !important;
}

.calendar-dark :deep(.fc-daygrid-day-number),
.calendar-dark :deep(.fc-col-header-cell-cushion),
.calendar-dark :deep(.fc-toolbar-title),
.calendar-dark :deep(.fc-list-event-title),
.calendar-dark :deep(.fc-list-day-text),
.calendar-dark :deep(.fc-list-day-side-text) {
  color: rgba(255, 255, 255, 0.87) !important;
}

.calendar-dark :deep(.fc-timegrid-slot-label-cushion) {
  color: rgba(255, 255, 255, 0.6) !important;
}

.calendar-dark :deep(.fc-daygrid-day.fc-day-today) {
  background: rgba(129, 140, 248, 0.12) !important;
}

.calendar-dark :deep(.fc-daygrid-day.fc-day-today .fc-daygrid-day-number) {
  background: #818cf8;
}

.calendar-dark :deep(.fc-button-primary) {
  background-color: #818cf8 !important;
  border-color: #818cf8 !important;
}

.calendar-dark :deep(.fc-button-primary:hover) {
  background-color: #6366f1 !important;
  border-color: #6366f1 !important;
}

.calendar-dark :deep(.fc-button-active) {
  background-color: #4f46e5 !important;
  border-color: #4f46e5 !important;
}

.calendar-dark :deep(.fc-list-day-cushion) {
  background: rgba(255, 255, 255, 0.05) !important;
}

.calendar-dark :deep(.fc-list-event:hover td) {
  background: rgba(129, 140, 248, 0.1);
}

.calendar-dark :deep(.fc-timegrid-now-indicator-line) {
  border-color: #818cf8;
}

.calendar-dark :deep(.fc-timegrid-now-indicator-arrow) {
  border-top-color: #818cf8;
  border-bottom-color: #818cf8;
}

.calendar-dark :deep(.fc-highlight) {
  background: rgba(129, 140, 248, 0.2) !important;
}
</style>
