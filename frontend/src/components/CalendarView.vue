<template>
  <div class="cal-root">
    <!-- Toolbar -->
    <div class="flex items-center mb-4 flex-wrap gap-2">
      <div class="flex items-center gap-1">
        <button
          class="p-1.5 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          @click="prev"
        >
          <i class="mdi mdi-chevron-left text-lg" />
        </button>
        <button
          class="px-3 py-1 text-sm rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          @click="goToToday"
        >
          Today
        </button>
        <button
          class="p-1.5 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          @click="next"
        >
          <i class="mdi mdi-chevron-right text-lg" />
        </button>
      </div>
      <span class="text-lg font-bold ml-1 text-gray-900 dark:text-gray-100">{{ title }}</span>
      <div class="flex-1" />
      <!-- View toggle -->
      <div class="flex rounded-lg border border-gray-300 dark:border-gray-700 overflow-hidden">
        <button
          v-for="opt in viewOptions"
          :key="opt.value"
          :class="[
            'px-3 py-1 text-xs font-medium transition-colors',
            view === opt.value
              ? 'bg-blue-500 text-white'
              : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
          ]"
          @click="view = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Month View -->
    <template v-if="view === 'month'">
      <div class="cal-dow-header">
        <div v-for="d in DOW_HEADERS" :key="d" class="cal-dow-cell">{{ d }}</div>
      </div>
      <div class="cal-month-grid">
        <div
          v-for="(day, i) in monthDays"
          :key="i"
          :class="[
            'cal-day',
            !day.isCurrentMonth ? 'opacity-30' : '',
            day.isToday ? 'cal-day--today' : 'cal-day--normal'
          ]"
          @click="onDayClick(day)"
        >
          <div class="cal-day-num">
            <span :class="day.isToday ? 'cal-today-dot' : ''">{{ day.date.getDate() }}</span>
          </div>
          <div class="cal-events">
            <div
              v-for="ev in getDayEvents(day.date).slice(0, 3)"
              :key="ev.id"
              class="cal-event"
              :style="{ backgroundColor: ev.backgroundColor || '#3b82f6' }"
              @click.stop="onEventClick(ev)"
            >
              <span v-if="!ev.allDay" class="cal-event-time">{{ formatTime(ev.start) }}</span>
              {{ ev.title }}
              <span
                v-for="tag in (ev.extendedProps?.subtask_category_names || [])"
                :key="tag"
                class="cal-cat-tag"
              >{{ tag }}</span>
            </div>
            <div v-if="getDayEvents(day.date).length > 3" class="cal-event-more">
              +{{ getDayEvents(day.date).length - 3 }} more
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Week View -->
    <template v-else-if="view === 'week'">
      <div class="cal-week-grid">
        <div
          v-for="(day, i) in weekDays"
          :key="i"
          :class="[
            'cal-week-col',
            day.isToday ? 'cal-week-col--today' : ''
          ]"
        >
          <div class="cal-week-header" @click="onDayClick(day)">
            <div class="cal-week-dow">
              {{ DOW_SHORT[day.date.getDay()] }}
            </div>
            <div class="mt-1">
              <span :class="day.isToday ? 'cal-today-dot cal-today-dot--lg' : 'cal-week-daynum'">
                {{ day.date.getDate() }}
              </span>
            </div>
          </div>
          <div class="cal-week-events">
            <div
              v-for="ev in getDayEvents(day.date)"
              :key="ev.id"
              class="cal-event mb-1"
              :style="{ backgroundColor: ev.backgroundColor || '#3b82f6' }"
              @click.stop="onEventClick(ev)"
            >
              <div v-if="!ev.allDay" class="cal-event-time">{{ formatTime(ev.start) }}</div>
              {{ ev.title }}
              <div v-if="(ev.extendedProps?.subtask_category_names || []).length" class="cal-cat-tags">
                <span
                  v-for="tag in ev.extendedProps.subtask_category_names"
                  :key="tag"
                  class="cal-cat-tag"
                >{{ tag }}</span>
              </div>
            </div>
            <div v-if="getDayEvents(day.date).length === 0" class="cal-week-empty" @click="onDayClick(day)" />
          </div>
        </div>
      </div>
    </template>

    <!-- List View -->
    <template v-else>
      <div v-if="sortedListEvents.length === 0" class="text-center py-12">
        <i class="mdi mdi-calendar-blank-outline text-5xl text-gray-400 dark:text-gray-600 block mb-3" />
        <div class="text-sm text-gray-500 dark:text-gray-400">No upcoming events</div>
      </div>
      <template v-else>
        <template v-for="(group, dateStr) in groupedListEvents" :key="dateStr">
          <div class="cal-list-date">
            {{ dateStr }}
          </div>
          <div
            v-for="ev in group"
            :key="ev.id"
            class="cal-list-card"
            @click="onEventClick(ev)"
          >
            <div class="cal-list-dot" :style="{ backgroundColor: ev.backgroundColor || '#3b82f6' }" />
            <div class="flex-1 min-w-0">
              <div class="cal-list-title">{{ ev.title }}</div>
              <div class="cal-list-time">{{ ev.allDay ? 'All day' : formatTime(ev.start) }}</div>
              <div v-if="(ev.extendedProps?.subtask_category_names || []).length" class="cal-cat-tags mt-1">
                <span
                  v-for="tag in ev.extendedProps.subtask_category_names"
                  :key="tag"
                  class="cal-cat-tag-list"
                >{{ tag }}</span>
              </div>
            </div>
          </div>
        </template>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  events: { type: Array, default: () => [] },
})

const emit = defineEmits(['event-click', 'date-click', 'dates-set'])

const DOW_HEADERS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const DOW_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const viewOptions = [
  { value: 'month', label: 'Month' },
  { value: 'week', label: 'Week' },
  { value: 'list', label: 'List' },
]

const DAY_IN_MS = 24 * 60 * 60 * 1000
const DEFAULT_EVENT_DURATION_MS = 60 * 60 * 1000
const LIST_VIEW_RANGE_MS = 60 * DAY_IN_MS

const view = ref(localStorage.getItem('calendarView') || 'month')
const currentDate = ref(new Date())

watch(view, (val) => {
  localStorage.setItem('calendarView', val)
})

const todayDate = new Date()
todayDate.setHours(0, 0, 0, 0)

function isSameDay(a, b) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

const title = computed(() => {
  if (view.value === 'month') {
    return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }
  if (view.value === 'week') {
    const days = weekDays.value
    const start = days[0].date
    const end = days[days.length - 1].date
    if (start.getMonth() === end.getMonth()) {
      return `${start.toLocaleDateString('en-US', { month: 'long' })} ${start.getDate()} \u2013 ${end.getDate()}, ${start.getFullYear()}`
    }
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} \u2013 ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  }
  return 'Upcoming Events'
})

const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDow = (firstDay.getDay() + 6) % 7

  const days = []
  for (let i = startDow; i > 0; i--) {
    const d = new Date(year, month, 1 - i)
    days.push({ date: d, isCurrentMonth: false, isToday: isSameDay(d, todayDate) })
  }
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const d = new Date(year, month, i)
    days.push({ date: d, isCurrentMonth: true, isToday: isSameDay(d, todayDate) })
  }
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const d = new Date(year, month + 1, i)
    days.push({ date: d, isCurrentMonth: false, isToday: isSameDay(d, todayDate) })
  }
  return days
})

const weekDays = computed(() => {
  const d = new Date(currentDate.value)
  const dow = (d.getDay() + 6) % 7
  d.setDate(d.getDate() - dow)
  return Array.from({ length: 7 }, (_, i) => {
    const day = new Date(d)
    day.setDate(d.getDate() + i)
    return { date: day, isCurrentMonth: true, isToday: isSameDay(day, todayDate) }
  })
})

function getDayEvents(date) {
  const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const dayEnd = new Date(dayStart.getTime() + DAY_IN_MS)
  return props.events.filter((ev) => {
    const start = new Date(ev.start)
    const end = ev.end ? new Date(ev.end) : new Date(start.getTime() + DEFAULT_EVENT_DURATION_MS)
    return start < dayEnd && end > dayStart
  })
}

const sortedListEvents = computed(() =>
  [...props.events].sort((a, b) => new Date(a.start) - new Date(b.start))
)

const groupedListEvents = computed(() => {
  const groups = {}
  for (const ev of sortedListEvents.value) {
    const key = new Date(ev.start).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
    if (!groups[key]) groups[key] = []
    groups[key].push(ev)
  }
  return groups
})

function formatTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
}

function prev() {
  const d = new Date(currentDate.value)
  if (view.value === 'month') d.setMonth(d.getMonth() - 1)
  else if (view.value === 'week') d.setDate(d.getDate() - 7)
  currentDate.value = d
}

function next() {
  const d = new Date(currentDate.value)
  if (view.value === 'month') d.setMonth(d.getMonth() + 1)
  else if (view.value === 'week') d.setDate(d.getDate() + 7)
  currentDate.value = d
}

function goToToday() {
  currentDate.value = new Date()
}

function emitDatesSet() {
  let start, end
  if (view.value === 'month') {
    const days = monthDays.value
    start = new Date(days[0].date)
    end = new Date(days[days.length - 1].date.getTime() + DAY_IN_MS)
  } else if (view.value === 'week') {
    const days = weekDays.value
    start = new Date(days[0].date)
    end = new Date(days[days.length - 1].date.getTime() + DAY_IN_MS)
  } else {
    start = new Date()
    start.setHours(0, 0, 0, 0)
    end = new Date(start.getTime() + LIST_VIEW_RANGE_MS)
  }
  emit('dates-set', { start, end })
}

function onDayClick(day) {
  emit('date-click', { dateStr: day.date.toISOString(), allDay: true })
}

function onEventClick(event) {
  emit('event-click', { event })
}

watch([view, currentDate], emitDatesSet)
onMounted(emitDatesSet)
</script>

<style scoped>
/* ── DOW header ─────────────────────────────────────────── */
.cal-dow-header {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  margin-bottom: 3px;
}

.cal-dow-cell {
  text-align: center;
  padding: 6px 0;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6b7280;
}
:global(.dark) .cal-dow-cell {
  color: #9ca3af;
}

/* ── Month grid ─────────────────────────────────────────── */
.cal-month-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 3px;
}

.cal-day {
  min-height: 96px;
  padding: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid #e5e7eb;
}
:global(.dark) .cal-day {
  border-color: #374151;
}

.cal-day--normal {
  background: #f9fafb;
}
.cal-day--normal:hover {
  background: #eff6ff;
}
:global(.dark) .cal-day--normal {
  background: #1f2937;
}
:global(.dark) .cal-day--normal:hover {
  background: #374151;
}

.cal-day--today {
  background: #eff6ff !important;
  border-color: #bfdbfe !important;
}
:global(.dark) .cal-day--today {
  background: #1e3a8a1a !important;
  border-color: #1e3a8a !important;
}

/* ── Day number ─────────────────────────────────────────── */
.cal-day-num {
  display: flex;
  justify-content: flex-end;
  padding: 0 2px 3px;
  font-size: 0.82rem;
  font-weight: 500;
  color: #4b5563;
}
:global(.dark) .cal-day-num {
  color: #9ca3af;
}

.cal-today-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #3b82f6;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.82rem;
}

.cal-today-dot--lg {
  width: 32px;
  height: 32px;
  font-size: 1rem;
}

/* ── Event pills ─────────────────────────────────────────── */
.cal-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cal-event {
  font-size: 0.72rem;
  font-weight: 500;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  transition: opacity 0.15s;
  line-height: 1.4;
}

.cal-event:hover {
  opacity: 0.85;
}

.cal-event-time {
  font-weight: 400;
  opacity: 0.85;
  margin-right: 2px;
}

.cal-event-more {
  font-size: 0.7rem;
  padding-left: 4px;
  color: #6b7280;
}
:global(.dark) .cal-event-more {
  color: #9ca3af;
}

/* ── Week view ─────────────────────────────────────────── */
.cal-week-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 4px;
  overflow-x: auto;
}

.cal-week-col {
  min-height: 360px;
  min-width: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}
:global(.dark) .cal-week-col {
  background: #1f2937;
  border-color: #374151;
}

.cal-week-col--today {
  background: #eff6ff !important;
  border-color: #bfdbfe !important;
}
:global(.dark) .cal-week-col--today {
  background: #172554 !important;
  border-color: #1e3a8a !important;
}

.cal-week-header {
  padding: 10px 8px;
  text-align: center;
  cursor: pointer;
  border-bottom: 1px solid #e5e7eb;
  user-select: none;
}
:global(.dark) .cal-week-header {
  border-bottom-color: #374151;
}

.cal-week-dow {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6b7280;
}
:global(.dark) .cal-week-dow {
  color: #9ca3af;
}

.cal-week-daynum {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
}
:global(.dark) .cal-week-daynum {
  color: #f3f4f6;
}

.cal-week-events {
  padding: 6px;
  display: flex;
  flex-direction: column;
}

.cal-week-empty {
  flex: 1;
  min-height: 60px;
  cursor: pointer;
}

/* ── Category tags ─────────────────────────────────────────── */
.cal-cat-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  margin-top: 2px;
}

.cal-cat-tag {
  display: inline-block;
  font-size: 0.6rem;
  font-weight: 600;
  padding: 0 4px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
  letter-spacing: 0.03em;
  line-height: 1.5;
  vertical-align: middle;
  margin-left: 2px;
}

.cal-cat-tag-list {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: #eff6ff;
  color: #3b82f6;
  letter-spacing: 0.03em;
  line-height: 1.5;
}
:global(.dark) .cal-cat-tag-list {
  background: #1e3a8a33;
  color: #93c5fd;
}

/* ── List view ─────────────────────────────────────────── */
.cal-list-date {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6b7280;
  padding: 12px 4px 4px;
}
:global(.dark) .cal-list-date {
  color: #9ca3af;
}

.cal-list-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: background 0.15s;
  background: #ffffff;
}
.cal-list-card:hover {
  background: #f9fafb;
}
:global(.dark) .cal-list-card {
  background: #1f2937;
  border-color: #374151;
}
:global(.dark) .cal-list-card:hover {
  background: #374151;
}

.cal-list-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cal-list-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
}
:global(.dark) .cal-list-title {
  color: #f3f4f6;
}

.cal-list-time {
  font-size: 0.75rem;
  color: #6b7280;
}
:global(.dark) .cal-list-time {
  color: #9ca3af;
}
</style>


