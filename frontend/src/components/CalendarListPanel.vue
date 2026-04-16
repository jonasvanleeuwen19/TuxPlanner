<template>
  <div>
    <div class="flex items-center mb-2 px-1">
      <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">My Calendars</span>
      <div class="flex-1" />
      <button
        class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-blue-500 transition-colors"
        @click="openAddDialog"
      >
        <i class="mdi mdi-plus text-sm" />
      </button>
    </div>

    <div
      v-for="list in calendarLists"
      :key="list.id"
      class="flex items-center px-1 py-1.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
    >
      <div class="w-3 h-3 rounded mr-2 shrink-0" :style="{ backgroundColor: list.color }" />
      <span class="text-xs flex-1 truncate">{{ list.name }}</span>
      <div class="flex items-center gap-1">
        <button
          v-if="!list.is_virtual"
          class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          @click="openEditDialog(list)"
        >
          <i class="mdi mdi-pencil-outline text-xs text-gray-500" />
        </button>
        <span v-if="list.is_virtual" class="text-xs px-1 text-gray-400 dark:text-gray-500 italic">auto</span>
        <button
          :class="[
            'relative inline-flex h-4 w-7 items-center rounded-full transition-colors shrink-0',
            list.is_visible ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
          ]"
          @click="list.is_virtual ? emit('toggle-virtual', list) : toggleVisibility(list)"
        >
          <span
            :class="[
              'inline-block h-3 w-3 transform rounded-full bg-white transition-transform',
              list.is_visible ? 'translate-x-3.5' : 'translate-x-0.5'
            ]"
          />
        </button>
      </div>
    </div>

    <!-- Add Dialog -->
    <Teleport to="body">
      <div
        v-if="addDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="addDialog = false"
      >
        <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-sm">
          <div class="flex items-center p-5 pb-3">
            <span class="text-base font-bold text-gray-900 dark:text-gray-100">New Calendar List</span>
            <div class="flex-1" />
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400" @click="addDialog = false">
              <i class="mdi mdi-close" />
            </button>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="p-5 space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
              <input
                v-model="addForm.name"
                type="text"
                autofocus
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p v-if="addError" class="text-xs text-red-500 mt-1">{{ addError }}</p>
            </div>
            <div>
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Color</p>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="color in colorOptions"
                  :key="color"
                  class="w-6 h-6 rounded-full cursor-pointer transition-transform border-2 hover:scale-110 shrink-0"
                  :style="{ backgroundColor: color, borderColor: addForm.color === color ? 'rgba(0,0,0,0.4)' : 'transparent' }"
                  @click="addForm.color = color"
                />
              </div>
            </div>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="flex justify-end gap-2 p-4">
            <button
              class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              @click="addDialog = false"
            >
              Cancel
            </button>
            <button
              :disabled="saving"
              class="flex items-center gap-1 px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              @click="saveAdd"
            >
              <i v-if="saving" class="mdi mdi-loading animate-spin" />
              Create
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Edit Dialog -->
    <Teleport to="body">
      <div
        v-if="editDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="editDialog = false"
      >
        <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-sm">
          <div class="flex items-center p-5 pb-3">
            <span class="text-base font-bold text-gray-900 dark:text-gray-100">Edit Calendar List</span>
            <div class="flex-1" />
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400" @click="editDialog = false">
              <i class="mdi mdi-close" />
            </button>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="p-5 space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
              <input
                v-model="editForm.name"
                type="text"
                :disabled="!!editForm.ical_feed_id"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <p v-if="editForm.ical_feed_id" class="text-xs text-gray-500 mt-1">Name is managed by ICAL feed</p>
              <p v-if="editError" class="text-xs text-red-500 mt-1">{{ editError }}</p>
            </div>
            <div>
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Color</p>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="color in colorOptions"
                  :key="color"
                  class="w-6 h-6 rounded-full cursor-pointer transition-transform border-2 hover:scale-110 shrink-0"
                  :style="{ backgroundColor: color, borderColor: editForm.color === color ? 'rgba(0,0,0,0.4)' : 'transparent' }"
                  @click="editForm.color = color"
                />
              </div>
            </div>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="flex items-center gap-2 p-4">
            <button
              v-if="!editForm.ical_feed_id"
              class="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors"
              @click="deleteList"
            >
              <i class="mdi mdi-trash-can" />
            </button>
            <div class="flex-1" />
            <button
              class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              @click="editDialog = false"
            >
              Cancel
            </button>
            <button
              :disabled="saving"
              class="flex items-center gap-1 px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              @click="saveEdit"
            >
              <i v-if="saving" class="mdi mdi-loading animate-spin" />
              Save
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { calendarListsApi } from '../api/index.js'

const props = defineProps({
  calendarLists: { type: Array, default: () => [] },
})

const emit = defineEmits(['update', 'toggle-virtual'])

const colorOptions = [
  '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#ef4444', '#ec4899', '#0ea5e9',
  '#84cc16', '#f97316', '#64748b', '#a855f7',
]

const addDialog = ref(false)
const editDialog = ref(false)
const saving = ref(false)
const addError = ref('')
const editError = ref('')

const addForm = ref({ name: '', color: '#3b82f6' })
const editForm = ref({ id: null, name: '', color: '#3b82f6', ical_feed_id: null })

function openAddDialog() {
  addForm.value = { name: '', color: '#3b82f6' }
  addError.value = ''
  addDialog.value = true
}

function openEditDialog(list) {
  editForm.value = { id: list.id, name: list.name, color: list.color, ical_feed_id: list.ical_feed_id }
  editError.value = ''
  editDialog.value = true
}

async function toggleVisibility(list) {
  try {
    await calendarListsApi.update(list.id, { is_visible: !list.is_visible })
    emit('update')
  } catch (err) {
    console.error('Failed to toggle visibility', err)
  }
}

async function saveAdd() {
  addError.value = ''
  if (!addForm.value.name) { addError.value = 'Name is required'; return }
  saving.value = true
  try {
    await calendarListsApi.create(addForm.value)
    addDialog.value = false
    emit('update')
  } catch (err) {
    console.error('Failed to create calendar list', err)
  } finally {
    saving.value = false
  }
}

async function saveEdit() {
  editError.value = ''
  if (!editForm.value.ical_feed_id && !editForm.value.name) { editError.value = 'Name is required'; return }
  saving.value = true
  try {
    const updates = { color: editForm.value.color }
    if (!editForm.value.ical_feed_id) updates.name = editForm.value.name
    await calendarListsApi.update(editForm.value.id, updates)
    editDialog.value = false
    emit('update')
  } catch (err) {
    console.error('Failed to update calendar list', err)
  } finally {
    saving.value = false
  }
}

async function deleteList() {
  try {
    await calendarListsApi.delete(editForm.value.id)
    editDialog.value = false
    emit('update')
  } catch (err) {
    console.error('Failed to delete calendar list', err)
  }
}
</script>
