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

          <!-- Subtasks (edit only) -->
          <template v-if="isEdit">
            <hr class="border-gray-200 dark:border-gray-700" />
            <div class="flex items-center">
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">Subtasks</span>
              <div class="flex-1" />
              <button
                class="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
                @click="openAddSubtask"
              >
                <i class="mdi mdi-plus text-sm" /> Add
              </button>
            </div>

            <div v-if="subtasksLoading" class="flex justify-center py-3">
              <i class="mdi mdi-loading animate-spin text-2xl text-blue-500" />
            </div>

            <div v-else class="space-y-1">
              <template v-for="(group, catName) in groupedSubtasks" :key="catName">
                <div class="text-[0.65rem] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 mt-2 mb-1">{{ catName }}</div>
                <div
                  v-for="subtask in group"
                  :key="subtask.id"
                  class="bg-gray-50 dark:bg-gray-800 rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <input
                      type="checkbox"
                      :checked="subtask.completed"
                      class="w-4 h-4 accent-blue-500 cursor-pointer shrink-0"
                      @change="toggleSubtask(subtask)"
                    />
                    <div class="flex-1 min-w-0">
                      <span
                        class="text-sm"
                        :class="subtask.completed ? 'line-through text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-gray-100'"
                      >{{ subtask.title }}</span>
                      <div v-if="subtask.description && expandedSubtask !== subtask.id" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 whitespace-pre-wrap">{{ subtask.description }}</div>
                    </div>
                    <button
                      class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-400 dark:text-gray-500 transition-colors shrink-0"
                      @click="toggleExpandSubtask(subtask)"
                    >
                      <i :class="['mdi text-sm', expandedSubtask === subtask.id ? 'mdi-chevron-up' : 'mdi-pencil-outline']" />
                    </button>
                    <button
                      class="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors shrink-0"
                      @click="removeSubtask(subtask)"
                    >
                      <i class="mdi mdi-close text-sm" />
                    </button>
                  </div>
                  <div v-if="expandedSubtask === subtask.id" class="mt-2 space-y-2">
                    <MarkdownEditor
                      v-model="subtask.description"
                      label="Subtask description"
                      placeholder="Add subtask notes (Markdown supported)…"
                      :rows="2"
                    />
                    <div class="flex gap-2">
                      <button class="px-3 py-1 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors" @click="saveSubtaskDescription(subtask)">Save</button>
                      <button class="px-3 py-1 text-xs font-medium rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" @click="expandedSubtask = null">Cancel</button>
                    </div>
                  </div>
                </div>
              </template>
              <p v-if="subtasks.length === 0" class="text-sm text-gray-400 dark:text-gray-500 py-1">No subtasks yet.</p>
            </div>

            <!-- Add subtask inline form -->
            <div v-if="addingSubtask" class="space-y-2 border border-gray-200 dark:border-gray-700 rounded-lg p-3">
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                  <select
                    v-model="newSubtask.category_id"
                    class="w-full px-2 py-1.5 text-xs border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option :value="null">No category</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Title</label>
                  <input
                    v-model="newSubtask.title"
                    type="text"
                    autofocus
                    class="w-full px-2 py-1.5 text-xs border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    @keyup.enter="saveSubtask"
                  />
                </div>
              </div>
              <MarkdownEditor
                v-model="newSubtask.description"
                label="Subtask description (optional)"
                placeholder="Add subtask notes (Markdown supported)…"
                :rows="2"
              />
              <div class="flex gap-2 items-center">
                <button class="px-3 py-1 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors" @click="saveSubtask">Save</button>
                <button class="px-3 py-1 text-xs font-medium rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" @click="addingSubtask = false">Cancel</button>
                <div class="flex-1" />
                <button
                  class="flex items-center gap-1 px-2 py-1 text-xs text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                  @click="manageCategoriesDialog = true"
                >
                  <i class="mdi mdi-tag-plus-outline" /> Manage categories
                </button>
              </div>
            </div>
          </template>
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

  <!-- Manage Categories dialog -->
  <Teleport to="body">
    <div
      v-if="manageCategoriesDialog"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60"
      @click.self="manageCategoriesDialog = false"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-sm">
        <div class="flex items-center p-5 pb-3">
          <span class="text-base font-bold text-gray-900 dark:text-gray-100">Subtask Categories</span>
          <div class="flex-1" />
          <button
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
            @click="manageCategoriesDialog = false"
          >
            <i class="mdi mdi-close text-lg" />
          </button>
        </div>
        <hr class="border-gray-200 dark:border-gray-700" />
        <div class="p-4 space-y-1 max-h-60 overflow-y-auto">
          <div
            v-for="cat in categories"
            :key="cat.id"
            class="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <i class="mdi mdi-tag-outline text-xs text-gray-400 dark:text-gray-500" />
            <span class="flex-1 text-sm text-gray-900 dark:text-gray-100">{{ cat.name }}</span>
            <button
              class="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors"
              @click="deleteCategory(cat)"
            >
              <i class="mdi mdi-trash-can-outline text-sm" />
            </button>
          </div>
          <p v-if="categories.length === 0" class="text-sm text-gray-400 dark:text-gray-500 text-center py-2">No categories yet.</p>
        </div>
        <div class="p-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex gap-2">
            <input
              v-model="newCategoryName"
              type="text"
              placeholder="New category name"
              class="flex-1 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              @keyup.enter="addCategory"
            />
            <button
              class="px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
              @click="addCategory"
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { subtasksApi, subtaskCategoriesApi } from '../api/index.js'
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
  props.calendarLists.filter((l) => l.name !== "TODO's")
)

const subtasks = ref([])
const subtasksLoading = ref(false)
const addingSubtask = ref(false)
const newSubtask = ref({ title: '', description: '', category_id: null })
const expandedSubtask = ref(null)

const categories = ref([])
const manageCategoriesDialog = ref(false)
const newCategoryName = ref('')

const groupedSubtasks = computed(() => {
  const groups = {}
  for (const subtask of subtasks.value) {
    const cat = subtask.category_id ? categories.value.find((c) => c.id === subtask.category_id) : null
    const key = cat ? cat.name : 'Uncategorized'
    if (!groups[key]) groups[key] = []
    groups[key].push(subtask)
  }
  return groups
})

watch(
  () => props.event,
  async (newEvent) => {
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
      if (newEvent.id) {
        await fetchSubtasks(newEvent.id)
      }
    } else {
      form.value = defaultForm()
      subtasks.value = []
      errors.value = {}
    }
  },
  { immediate: true }
)

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      await fetchCategories()
    } else {
      addingSubtask.value = false
      expandedSubtask.value = null
    }
  }
)

async function fetchSubtasks(eventId) {
  subtasksLoading.value = true
  try {
    const { data } = await subtasksApi.list(eventId)
    subtasks.value = data
  } catch (err) {
    console.error('Failed to fetch subtasks', err)
  } finally {
    subtasksLoading.value = false
  }
}

async function fetchCategories() {
  try {
    const { data } = await subtaskCategoriesApi.list()
    categories.value = data
  } catch (err) {
    console.error('Failed to fetch categories', err)
  }
}

function openAddSubtask() {
  newSubtask.value = { title: '', description: '', category_id: null }
  addingSubtask.value = true
}

async function saveSubtask() {
  if (!newSubtask.value.title.trim()) return
  try {
    const { data } = await subtasksApi.create(form.value.id, {
      title: newSubtask.value.title,
      description: newSubtask.value.description || null,
      category_id: newSubtask.value.category_id,
    })
    subtasks.value.push(data)
    newSubtask.value = { title: '', description: '', category_id: null }
    addingSubtask.value = false
  } catch (err) {
    console.error('Failed to create subtask', err)
  }
}

async function toggleSubtask(subtask) {
  try {
    const { data } = await subtasksApi.update(form.value.id, subtask.id, { completed: !subtask.completed })
    const idx = subtasks.value.findIndex((s) => s.id === subtask.id)
    if (idx !== -1) subtasks.value[idx] = data
  } catch (err) {
    console.error('Failed to toggle subtask', err)
  }
}

async function removeSubtask(subtask) {
  try {
    await subtasksApi.delete(form.value.id, subtask.id)
    subtasks.value = subtasks.value.filter((s) => s.id !== subtask.id)
    if (expandedSubtask.value === subtask.id) expandedSubtask.value = null
  } catch (err) {
    console.error('Failed to delete subtask', err)
  }
}

function toggleExpandSubtask(subtask) {
  expandedSubtask.value = expandedSubtask.value === subtask.id ? null : subtask.id
}

async function saveSubtaskDescription(subtask) {
  try {
    const { data } = await subtasksApi.update(form.value.id, subtask.id, { description: subtask.description || null })
    const idx = subtasks.value.findIndex((s) => s.id === subtask.id)
    if (idx !== -1) subtasks.value[idx] = data
    expandedSubtask.value = null
  } catch (err) {
    console.error('Failed to update subtask description', err)
  }
}

async function addCategory() {
  if (!newCategoryName.value.trim()) return
  try {
    const { data } = await subtaskCategoriesApi.create({ name: newCategoryName.value.trim() })
    categories.value.push(data)
    newCategoryName.value = ''
  } catch (err) {
    console.error('Failed to create category', err)
  }
}

async function deleteCategory(cat) {
  try {
    await subtaskCategoriesApi.delete(cat.id)
    categories.value = categories.value.filter((c) => c.id !== cat.id)
    if (form.value.id) await fetchSubtasks(form.value.id)
  } catch (err) {
    console.error('Failed to delete category', err)
  }
}

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
