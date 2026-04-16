<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="$emit('update:modelValue', false)"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg flex flex-col overflow-hidden max-h-[90vh]">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3 shrink-0">
          <div class="w-9 h-9 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-3 shrink-0">
            <i class="mdi mdi-calendar-clock text-lg text-purple-500 dark:text-purple-400" />
          </div>
          <span class="text-base font-bold text-gray-900 dark:text-gray-100">
            {{ editSession ? 'Edit Work Session' : 'Plan Work Sessions' }}
          </span>
          <div class="flex-1" />
          <button
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            <i class="mdi mdi-close text-lg" />
          </button>
        </div>
        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- EDIT MODE: single session form -->
        <template v-if="editSession">
          <div class="p-5 space-y-4 overflow-y-auto flex-1">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Start *</label>
              <div class="relative">
                <i class="mdi mdi-clock-start absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
                <input
                  v-model="editForm.start"
                  type="datetime-local"
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <p v-if="editStartError" class="text-xs text-red-500 mt-1">{{ editStartError }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">End</label>
              <div class="relative">
                <i class="mdi mdi-clock-end absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
                <input
                  v-model="editForm.end"
                  type="datetime-local"
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Note</label>
              <input
                v-model="editForm.note"
                type="text"
                placeholder="Optional note for this session"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          <hr class="border-gray-200 dark:border-gray-700 shrink-0" />
          <div class="flex justify-end gap-2 p-4 shrink-0">
            <button class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors" @click="$emit('update:modelValue', false)">Cancel</button>
            <button class="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors" @click="submitEdit">Save Changes</button>
          </div>
        </template>

        <!-- ADD MODE: step 1 = pick days, step 2 = set duration + note per day -->
        <template v-else>
          <!-- Step indicator -->
          <div class="flex items-center gap-2 px-5 pt-4 pb-2 shrink-0">
            <div :class="['w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center', step === 1 ? 'bg-purple-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500']">1</div>
            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Select Days</span>
            <div class="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
            <div :class="['w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center', step === 2 ? 'bg-purple-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500']">2</div>
            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Set Duration & Notes</span>
          </div>

          <!-- Step 1: Calendar picker -->
          <div v-if="step === 1" class="p-5 overflow-y-auto flex-1">
            <!-- Month navigation -->
            <div class="flex items-center justify-between mb-3">
              <button class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" @click="prevMonth">
                <i class="mdi mdi-chevron-left text-gray-600 dark:text-gray-400" />
              </button>
              <span class="text-sm font-semibold text-gray-800 dark:text-gray-200">{{ monthLabel }}</span>
              <button class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" @click="nextMonth">
                <i class="mdi mdi-chevron-right text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            <!-- Day-of-week headers -->
            <div class="grid grid-cols-7 mb-1">
              <div v-for="d in ['Mo','Tu','We','Th','Fr','Sa','Su']" :key="d" class="text-center text-xs text-gray-400 dark:text-gray-500 font-medium py-1">{{ d }}</div>
            </div>
            <!-- Calendar grid -->
            <div class="grid grid-cols-7 gap-1">
              <div v-for="(cell, i) in calendarCells" :key="i">
                <button
                  v-if="cell"
                  :class="[
                    'w-full aspect-square rounded-lg text-sm font-medium transition-colors flex items-center justify-center',
                    isPast(cell) ? 'text-gray-300 dark:text-gray-600 cursor-not-allowed' :
                    selectedDays.has(cell) ? 'bg-purple-500 text-white' :
                    isToday(cell) ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 hover:bg-purple-200 dark:hover:bg-purple-900/50' :
                    'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  ]"
                  :disabled="isPast(cell)"
                  @click="toggleDay(cell)"
                >
                  {{ new Date(cell + 'T00:00:00').getDate() }}
                </button>
                <div v-else class="w-full aspect-square" />
              </div>
            </div>
            <p v-if="selectedDays.size > 0" class="text-xs text-purple-600 dark:text-purple-400 mt-3 font-medium">
              {{ selectedDays.size }} day{{ selectedDays.size === 1 ? '' : 's' }} selected
            </p>
            <p v-else class="text-xs text-gray-400 dark:text-gray-500 mt-3">Click on days to select them</p>
          </div>

          <!-- Step 2: Per-day duration + note -->
          <div v-if="step === 2" class="p-5 overflow-y-auto flex-1 space-y-3">
            <div
              v-for="day in sortedSelectedDays"
              :key="day"
              class="bg-purple-50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-900/30 rounded-xl p-3"
            >
              <div class="flex items-center mb-2">
                <i class="mdi mdi-calendar text-purple-500 dark:text-purple-400 mr-2 text-sm" />
                <span class="text-sm font-semibold text-gray-800 dark:text-gray-200">{{ formatDayLabel(day) }}</span>
              </div>
              <div class="flex gap-2 mb-2">
                <div class="flex-1">
                  <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Hours</label>
                  <input
                    v-model.number="dayConfigs[day].hours"
                    type="number"
                    min="0"
                    max="23"
                    placeholder="0"
                    class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div class="flex-1">
                  <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Minutes</label>
                  <input
                    v-model.number="dayConfigs[day].minutes"
                    type="number"
                    min="0"
                    max="59"
                    placeholder="0"
                    class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Note</label>
                <input
                  v-model="dayConfigs[day].note"
                  type="text"
                  placeholder="Optional note"
                  class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <p v-if="dayErrors[day]" class="text-xs text-red-500 mt-1">{{ dayErrors[day] }}</p>
            </div>
          </div>

          <hr class="border-gray-200 dark:border-gray-700 shrink-0" />
          <div class="flex justify-between gap-2 p-4 shrink-0">
            <button
              v-if="step === 2"
              class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              @click="step = 1"
            >
              <i class="mdi mdi-arrow-left mr-1" />Back
            </button>
            <button class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors" @click="$emit('update:modelValue', false)">Cancel</button>
            <div class="flex-1" />
            <button
              v-if="step === 1"
              :disabled="selectedDays.size === 0"
              :class="['px-4 py-2 text-sm rounded-lg font-medium transition-colors', selectedDays.size === 0 ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed' : 'bg-purple-500 hover:bg-purple-600 text-white']"
              @click="goToStep2"
            >
              Next <i class="mdi mdi-arrow-right ml-1" />
            </button>
            <button
              v-if="step === 2"
              class="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors"
              @click="submitMulti"
            >
              Add {{ selectedDays.size }} Session{{ selectedDays.size === 1 ? '' : 's' }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  editSession: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'save'])

// ── Edit mode ────────────────────────────────────────────────
const editForm = ref({ start: '', end: '', note: '' })
const editStartError = ref('')

function formFromSession(session) {
  return {
    start: session.start ? new Date(session.start).toISOString().slice(0, 16) : '',
    end: session.end ? new Date(session.end).toISOString().slice(0, 16) : '',
    note: session.note || '',
  }
}

function submitEdit() {
  editStartError.value = ''
  if (!editForm.value.start) {
    editStartError.value = 'Start time is required'
    return
  }
  emit('save', {
    start: new Date(editForm.value.start).toISOString(),
    end: editForm.value.end ? new Date(editForm.value.end).toISOString() : null,
    note: editForm.value.note || null,
  })
}

// ── Add mode ─────────────────────────────────────────────────
const step = ref(1)
const selectedDays = ref(new Set())
const dayConfigs = ref({})
const dayErrors = ref({})

// Calendar navigation
const today = new Date()
const calViewYear = ref(today.getFullYear())
const calViewMonth = ref(today.getMonth()) // 0-indexed

const monthLabel = computed(() =>
  new Date(calViewYear.value, calViewMonth.value, 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
)

const calendarCells = computed(() => {
  const year = calViewYear.value
  const month = calViewMonth.value
  const firstDay = new Date(year, month, 1)
  // Monday=0 offset
  const startOffset = (firstDay.getDay() + 6) % 7
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < startOffset; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) {
    const mm = String(month + 1).padStart(2, '0')
    const dd = String(d).padStart(2, '0')
    cells.push(`${year}-${mm}-${dd}`)
  }
  return cells
})

const todayStr = computed(() => {
  const t = new Date()
  return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')}`
})

function isToday(dateStr) { return dateStr === todayStr.value }
function isPast(dateStr) { return dateStr < todayStr.value }

function toggleDay(dateStr) {
  const next = new Set(selectedDays.value)
  if (next.has(dateStr)) next.delete(dateStr)
  else next.add(dateStr)
  selectedDays.value = next
}

function prevMonth() {
  if (calViewMonth.value === 0) { calViewYear.value--; calViewMonth.value = 11 }
  else calViewMonth.value--
}

function nextMonth() {
  if (calViewMonth.value === 11) { calViewYear.value++; calViewMonth.value = 0 }
  else calViewMonth.value++
}

const sortedSelectedDays = computed(() =>
  [...selectedDays.value].sort()
)

function formatDayLabel(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
}

function goToStep2() {
  // Ensure dayConfigs entries exist for all selected days
  for (const day of selectedDays.value) {
    if (!dayConfigs.value[day]) {
      dayConfigs.value[day] = { hours: 1, minutes: 0, note: '' }
    }
  }
  // Remove configs for deselected days
  for (const key of Object.keys(dayConfigs.value)) {
    if (!selectedDays.value.has(key)) delete dayConfigs.value[key]
  }
  dayErrors.value = {}
  step.value = 2
}

function submitMulti() {
  dayErrors.value = {}
  let valid = true
  for (const day of sortedSelectedDays.value) {
    const cfg = dayConfigs.value[day]
    const h = cfg?.hours ?? 0
    const m = cfg?.minutes ?? 0
    if ((h === 0 || h === '') && (m === 0 || m === '')) {
      dayErrors.value[day] = 'Please set at least 1 minute of work time'
      valid = false
    }
  }
  if (!valid) return

  const sessions = sortedSelectedDays.value.map((day) => {
    const cfg = dayConfigs.value[day]
    const start = new Date(day + 'T00:00:00')
    const totalMinutes = (Number(cfg.hours) || 0) * 60 + (Number(cfg.minutes) || 0)
    const end = new Date(start.getTime() + totalMinutes * 60 * 1000)
    return {
      start: start.toISOString(),
      end: end.toISOString(),
      note: cfg.note || null,
    }
  })

  emit('save', sessions)
}

// ── Reset on open/close ──────────────────────────────────────
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      step.value = 1
      selectedDays.value = new Set()
      dayConfigs.value = {}
      dayErrors.value = {}
      editStartError.value = ''
      const now = new Date()
      calViewYear.value = now.getFullYear()
      calViewMonth.value = now.getMonth()
      if (props.editSession) {
        editForm.value = formFromSession(props.editSession)
      } else {
        editForm.value = { start: '', end: '', note: '' }
      }
    }
  }
)

watch(
  () => props.editSession,
  (session) => {
    if (session && props.modelValue) {
      editForm.value = formFromSession(session)
    }
  }
)
</script>
