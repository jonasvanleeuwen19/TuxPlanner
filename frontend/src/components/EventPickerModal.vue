<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60"
      @click.self="$emit('update:modelValue', false)"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3 shrink-0">
          <div class="w-9 h-9 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-3 shrink-0">
            <i class="mdi mdi-calendar-link text-lg text-blue-500 dark:text-blue-400" />
          </div>
          <span class="text-base font-bold text-gray-900 dark:text-gray-100">Link Calendar Event</span>
          <div class="flex-1" />
          <button
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            <i class="mdi mdi-close text-lg" />
          </button>
        </div>
        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Calendar navigation -->
        <div class="flex items-center px-5 py-3 gap-2 shrink-0">
          <button
            class="p-1.5 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            @click="prevMonth"
          >
            <i class="mdi mdi-chevron-left text-lg" />
          </button>
          <span class="text-sm font-bold text-gray-900 dark:text-gray-100 flex-1 text-center">
            {{ monthTitle }}
          </span>
          <button
            class="p-1.5 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            @click="nextMonth"
          >
            <i class="mdi mdi-chevron-right text-lg" />
          </button>
        </div>

        <!-- DOW headers -->
        <div class="grid grid-cols-7 px-3 shrink-0">
          <div
            v-for="d in DOW_HEADERS"
            :key="d"
            class="text-center text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 pb-1"
          >
            {{ d }}
          </div>
        </div>

        <!-- Calendar grid -->
        <div class="grid grid-cols-7 gap-px px-3 pb-3 shrink-0">
          <div
            v-for="(day, i) in monthDays"
            :key="i"
            :class="[
              'min-h-[60px] rounded-lg p-1 cursor-pointer transition-colors',
              !day.isCurrentMonth ? 'opacity-30' : '',
              day.isToday ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800',
              selectedDay && isSameDay(day.date, selectedDay) ? 'ring-2 ring-blue-400' : ''
            ]"
            @click="selectDay(day)"
          >
            <div class="flex justify-end mb-0.5">
              <span
                :class="[
                  'text-xs font-medium w-5 h-5 flex items-center justify-center rounded-full',
                  day.isToday ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-400'
                ]"
              >{{ day.date.getDate() }}</span>
            </div>
            <div class="flex flex-col gap-0.5">
              <div
                v-for="ev in getDayEvents(day.date).slice(0, 2)"
                :key="ev.id"
                :class="[
                  'text-[10px] font-medium px-1 py-0.5 rounded truncate cursor-pointer transition-opacity',
                  selectedEventId === ev.id ? 'ring-2 ring-offset-1 ring-blue-400' : 'hover:opacity-80'
                ]"
                :style="{ backgroundColor: ev.color || '#3b82f6', color: '#fff' }"
                @click.stop="selectEvent(ev)"
              >
                {{ ev.title }}
              </div>
              <div
                v-if="getDayEvents(day.date).length > 2"
                class="text-[9px] text-gray-400 dark:text-gray-500 pl-1"
              >
                +{{ getDayEvents(day.date).length - 2 }} more
              </div>
            </div>
          </div>
        </div>

        <!-- Day events panel (shown when a day is selected and has events) -->
        <div v-if="selectedDay && getDayEvents(selectedDay).length > 0" class="border-t border-gray-200 dark:border-gray-700 shrink-0">
          <div class="px-5 py-3 max-h-40 overflow-y-auto space-y-1.5">
            <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
              {{ selectedDayLabel }} events
            </p>
            <div
              v-for="ev in getDayEvents(selectedDay)"
              :key="ev.id"
              :class="[
                'flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors border',
                selectedEventId === ev.id
                  ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-800'
              ]"
              @click="selectEvent(ev)"
            >
              <div class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: ev.color || '#3b82f6' }" />
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">{{ ev.title }}</p>
                <p class="text-xs text-gray-400 dark:text-gray-500">{{ formatEventTime(ev) }}</p>
              </div>
              <i v-if="selectedEventId === ev.id" class="mdi mdi-check-circle text-blue-500 text-sm shrink-0" />
            </div>
          </div>
        </div>

        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Footer -->
        <div class="flex items-center gap-2 p-4 shrink-0">
          <div class="flex-1 min-w-0">
            <span v-if="selectedEventId" class="text-xs text-gray-500 dark:text-gray-400">
              Selected: <span class="font-medium text-gray-800 dark:text-gray-200">{{ selectedEventTitle }}</span>
            </span>
            <span v-else class="text-xs text-gray-400 dark:text-gray-500">Click an event to select it</span>
          </div>
          <button
            v-if="selectedEventId"
            class="px-3 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            @click="clearSelection"
          >
            Remove link
          </button>
          <button
            class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            Cancel
          </button>
          <button
            class="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            @click="confirm"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  events: { type: Array, default: () => [] },
  initialEventId: { type: Number, default: null },
})

const emit = defineEmits(['update:modelValue', 'select'])

const DOW_HEADERS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const DAY_IN_MS = 24 * 60 * 60 * 1000
const DEFAULT_EVENT_DURATION_MS = 60 * 60 * 1000

const currentDate = ref(new Date())
const selectedDay = ref(null)
const selectedEventId = ref(null)

watch(() => props.modelValue, (val) => {
  if (val) {
    selectedEventId.value = props.initialEventId ?? null
    currentDate.value = new Date()
    selectedDay.value = null
    // Navigate to the month of the currently selected event
    if (props.initialEventId) {
      const ev = props.events.find((e) => e.id === props.initialEventId)
      if (ev?.start) {
        currentDate.value = new Date(ev.start)
      }
    }
  }
})

const monthTitle = computed(() =>
  currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
)

const todayDate = computed(() => {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  return d
})

function isSameDay(a, b) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDow = (firstDay.getDay() + 6) % 7

  const days = []
  for (let i = startDow; i > 0; i--) {
    const d = new Date(year, month, 1 - i)
    days.push({ date: d, isCurrentMonth: false, isToday: isSameDay(d, todayDate.value) })
  }
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const d = new Date(year, month, i)
    days.push({ date: d, isCurrentMonth: true, isToday: isSameDay(d, todayDate.value) })
  }
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const d = new Date(year, month + 1, i)
    days.push({ date: d, isCurrentMonth: false, isToday: isSameDay(d, todayDate.value) })
  }
  return days
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

function prevMonth() {
  const d = new Date(currentDate.value)
  d.setMonth(d.getMonth() - 1)
  currentDate.value = d
}

function nextMonth() {
  const d = new Date(currentDate.value)
  d.setMonth(d.getMonth() + 1)
  currentDate.value = d
}

function selectDay(day) {
  selectedDay.value = day.date
}

function selectEvent(ev) {
  selectedEventId.value = ev.id
}

function clearSelection() {
  selectedEventId.value = null
}

const selectedEventTitle = computed(() => {
  if (!selectedEventId.value) return ''
  const ev = props.events.find((e) => e.id === selectedEventId.value)
  return ev?.title || `Event #${selectedEventId.value}`
})

const selectedDayLabel = computed(() => {
  if (!selectedDay.value) return ''
  return selectedDay.value.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
})

function formatEventTime(ev) {
  if (!ev?.start) return ''
  if (ev.all_day) return 'All day'
  const start = new Date(ev.start)
  const time = start.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  if (ev.end) {
    const endTime = new Date(ev.end).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
    return `${time} – ${endTime}`
  }
  return time
}

function confirm() {
  emit('select', selectedEventId.value ?? null)
  emit('update:modelValue', false)
}
</script>
