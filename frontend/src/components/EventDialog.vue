<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="close"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3 shrink-0">
          <div class="w-9 h-9 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-3 shrink-0">
            <i :class="['mdi text-lg text-blue-500 dark:text-blue-400', isEdit ? 'mdi-calendar-edit' : 'mdi-calendar-plus']" />
          </div>
          <span class="text-base font-bold text-gray-900 dark:text-gray-100">{{ isEdit ? 'Edit Event' : 'New Event' }}</span>
          <div class="flex-1" />
          <button
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
            @click="close"
          >
            <i class="mdi mdi-close text-lg" />
          </button>
        </div>
        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Scrollable body -->
        <div class="overflow-y-auto flex-1 p-5 space-y-4">
          <!-- Title -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Title *</label>
            <div class="relative">
              <i class="mdi mdi-format-title absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.title"
                type="text"
                autofocus
                placeholder="Event title"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>
            <p v-if="errors.title" class="text-xs text-red-500 mt-1">{{ errors.title }}</p>
          </div>

          <!-- Description -->
          <MarkdownEditor
            v-model="form.description"
            label="Description"
            placeholder="Add a description (Markdown supported)…"
            :rows="3"
          />

          <!-- Location -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Location</label>
            <div class="relative">
              <i class="mdi mdi-map-marker-outline absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.location"
                type="text"
                placeholder="Location"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>
          </div>

          <!-- Calendar list -->
          <div v-if="!isIcalEvent">
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Calendar list</label>
            <div class="relative">
              <i class="mdi mdi-calendar-multiple absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <select
                v-model="form.calendar_list_id"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              >
                <option :value="null">No calendar</option>
                <option v-for="list in writableCalendarListItems" :key="list.id" :value="list.id">{{ list.name }}</option>
              </select>
            </div>
          </div>

          <!-- All day -->
          <div class="flex items-center gap-2">
            <input
              id="all-day-cb"
              v-model="form.all_day"
              type="checkbox"
              class="w-4 h-4 accent-blue-500 cursor-pointer"
            />
            <label for="all-day-cb" class="text-sm text-gray-700 dark:text-gray-300 cursor-pointer select-none">All day</label>
          </div>

          <!-- Start / End -->
          <div class="grid gap-3" :class="form.all_day ? 'grid-cols-1' : 'grid-cols-2'">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{{ form.all_day ? 'Date' : 'Start' }} *</label>
              <input
                v-model="form.start"
                :type="form.all_day ? 'date' : 'datetime-local'"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
              <p v-if="errors.start" class="text-xs text-red-500 mt-1">{{ errors.start }}</p>
            </div>
            <div v-if="!form.all_day">
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">End</label>
              <input
                v-model="form.end"
                type="datetime-local"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>
          </div>

          <!-- Color override -->
          <div v-if="!isIcalEvent" class="flex items-center gap-2 flex-wrap">
            <span class="text-xs text-gray-500 dark:text-gray-400 mr-1">Color override</span>
            <div
              v-for="color in colors"
              :key="color"
              class="w-6 h-6 rounded-full cursor-pointer transition-transform hover:scale-110 shrink-0 border-2"
              :style="{ backgroundColor: color, borderColor: form.color === color ? 'rgba(0,0,0,0.4)' : 'transparent' }"
              @click="form.color = form.color === color ? null : color"
            />
          </div>
        </div>

        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Actions -->
        <div class="flex items-center gap-2 p-4 shrink-0">
          <button
            v-if="isEdit && !isIcalEvent"
            class="flex items-center gap-1 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            @click="$emit('delete', form.id)"
          >
            <i class="mdi mdi-trash-can" /> Delete
          </button>
          <div
            v-if="isIcalEvent"
            class="flex items-center gap-1 px-2 py-0.5 text-xs rounded-md bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400"
          >
            <i class="mdi mdi-calendar-sync-outline" /> iCal event
          </div>
          <div class="flex-1" />
          <button
            class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            @click="close"
          >
            Cancel
          </button>
          <button
            v-if="!isIcalEvent"
            class="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            @click="submit"
          >
            {{ isEdit ? 'Save' : 'Create' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import MarkdownEditor from './MarkdownEditor.vue'

const props = defineProps({
  modelValue: Boolean,
  event: { type: Object, default: null },
  calendarLists: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'save', 'delete'])

const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#0ea5e9']

const errors = ref({})

const defaultForm = () => ({
  id: null,
  title: '',
  description: '',
  location: '',
  start: '',
  end: '',
  all_day: false,
  color: null,
  calendar_list_id: null,
})

const form = ref(defaultForm())

const isEdit = computed(() => !!form.value.id)
const isIcalEvent = computed(() => form.value.source === 'ical')

const writableCalendarListItems = computed(() =>
  props.calendarLists.filter((l) => l.name !== "TODO's" && !l.is_auto)
)

watch(
  () => props.event,
  (newEvent) => {
    if (newEvent) {
      form.value = {
        id: newEvent.id || null,
        title: newEvent.title || '',
        description: newEvent.description || '',
        location: newEvent.location || '',
        start: formatForInput(newEvent.start, newEvent.all_day),
        end: newEvent.end ? formatForInput(newEvent.end, newEvent.all_day) : '',
        all_day: newEvent.all_day || false,
        color: newEvent.color || null,
        source: newEvent.source || null,
        calendar_list_id: newEvent.calendar_list_id || null,
      }
      errors.value = {}
    } else {
      form.value = defaultForm()
      errors.value = {}
    }
  },
  { immediate: true }
)

function formatForInput(dateStr, allDay) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (allDay) {
    return d.toISOString().split('T')[0]
  }
  return d.toISOString().slice(0, 16)
}

function validate() {
  errors.value = {}
  if (!form.value.title.trim()) errors.value.title = 'Title is required'
  if (!form.value.start) errors.value.start = 'Start is required'
  return Object.keys(errors.value).length === 0
}

function submit() {
  if (!validate()) return
  emit('save', {
    ...form.value,
    start: new Date(form.value.start).toISOString(),
    end: form.value.end ? new Date(form.value.end).toISOString() : null,
    location: form.value.location || null,
    color: form.value.color || null,
  })
}

function close() {
  emit('update:modelValue', false)
}
</script>
