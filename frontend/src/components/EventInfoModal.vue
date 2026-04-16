<template>
  <Teleport to="body">
    <div
      v-if="modelValue && event"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="close"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3 shrink-0">
          <div
            class="w-3 h-3 rounded-full mr-3 shrink-0"
            :style="{ backgroundColor: event.backgroundColor || '#3b82f6' }"
          />
          <span class="text-base font-bold text-gray-900 dark:text-gray-100 flex-1 min-w-0 truncate">{{ event.title }}</span>
          <div class="flex items-center gap-1 ml-2 shrink-0">
            <button
              v-if="!isIcalEvent"
              class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
              @click="$emit('edit')"
            >
              <i class="mdi mdi-pencil-outline" /> Edit
            </button>
            <button
              class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
              @click="close"
            >
              <i class="mdi mdi-close text-lg" />
            </button>
          </div>
        </div>
        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Scrollable body -->
        <div class="overflow-y-auto flex-1 p-5 space-y-4">
          <!-- iCal badge -->
          <div
            v-if="isIcalEvent"
            class="flex items-center gap-1 px-2 py-0.5 w-fit text-xs rounded-md bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400"
          >
            <i class="mdi mdi-calendar-sync-outline" /> iCal event
          </div>

          <!-- Date/time -->
          <div class="flex items-start gap-2">
            <i class="mdi mdi-clock-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5" />
            <div>
              <p class="text-sm text-gray-900 dark:text-gray-100 font-medium">
                {{ formatEventDate(event) }}
              </p>
              <p v-if="event.allDay" class="text-xs text-gray-500 dark:text-gray-400">All day</p>
            </div>
          </div>

          <!-- Location -->
          <div v-if="eventLocation" class="flex items-start gap-2">
            <i class="mdi mdi-map-marker-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5" />
            <p class="text-sm text-gray-700 dark:text-gray-300">{{ eventLocation }}</p>
          </div>

          <!-- Description -->
          <div v-if="eventDescription" class="flex items-start gap-2">
            <i class="mdi mdi-text-box-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5" />
            <div
              class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm max-w-none dark:prose-invert flex-1"
              v-html="renderedDescription"
            />
          </div>

          <!-- Subtasks section -->
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
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { subtasksApi, subtaskCategoriesApi } from '../api/index.js'
import MarkdownEditor from './MarkdownEditor.vue'

const props = defineProps({
  modelValue: Boolean,
  event: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'edit'])

const isIcalEvent = computed(() => props.event?.extendedProps?.source === 'ical')

const eventDescription = computed(() => props.event?.extendedProps?.description || '')
const eventLocation = computed(() => props.event?.extendedProps?.location || '')

const renderedDescription = computed(() => {
  if (!eventDescription.value) return ''
  return DOMPurify.sanitize(marked.parse(eventDescription.value))
})

function formatEventDate(event) {
  if (!event?.start) return ''
  const start = new Date(event.start)
  if (event.allDay) {
    return start.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
  }
  const end = event.end ? new Date(event.end) : null
  const startStr = start.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  if (!end) return startStr
  const endStr = end.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  return `${startStr} – ${endStr}`
}

// Subtasks
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

const eventId = computed(() => props.event?.extendedProps?.raw?.id || null)

watch(
  () => props.modelValue,
  async (open) => {
    if (open && eventId.value) {
      await Promise.all([fetchSubtasks(eventId.value), fetchCategories()])
    } else if (!open) {
      addingSubtask.value = false
      expandedSubtask.value = null
    }
  }
)

async function fetchSubtasks(id) {
  subtasksLoading.value = true
  try {
    const { data } = await subtasksApi.list(id)
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
  if (!newSubtask.value.title.trim() || !eventId.value) return
  try {
    const { data } = await subtasksApi.create(eventId.value, {
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
  if (!eventId.value) return
  try {
    const { data } = await subtasksApi.update(eventId.value, subtask.id, { completed: !subtask.completed })
    const idx = subtasks.value.findIndex((s) => s.id === subtask.id)
    if (idx !== -1) subtasks.value[idx] = data
  } catch (err) {
    console.error('Failed to toggle subtask', err)
  }
}

async function removeSubtask(subtask) {
  if (!eventId.value) return
  try {
    await subtasksApi.delete(eventId.value, subtask.id)
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
  if (!eventId.value) return
  try {
    const { data } = await subtasksApi.update(eventId.value, subtask.id, { description: subtask.description || null })
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
    if (eventId.value) await fetchSubtasks(eventId.value)
  } catch (err) {
    console.error('Failed to delete category', err)
  }
}

function close() {
  emit('update:modelValue', false)
}
</script>
