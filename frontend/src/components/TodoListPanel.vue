<template>
  <div>
    <div class="flex items-center mb-2 px-1">
      <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">My Lists</span>
      <div class="flex-1" />
      <button
        class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-blue-500 transition-colors"
        @click="openAddDialog"
      >
        <i class="mdi mdi-plus text-sm" />
      </button>
    </div>

    <!-- "All tasks" virtual list -->
    <div
      :class="[
        'flex items-center px-2 py-1.5 rounded-lg cursor-pointer transition-colors',
        selectedListId === null ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
      ]"
      @click="$emit('select', null)"
    >
      <i class="mdi mdi-view-list text-xs mr-2 text-blue-500" />
      <span class="text-xs flex-1 truncate font-medium">All tasks</span>
      <span class="text-xs text-gray-400 dark:text-gray-500">{{ todoLists.reduce((s, l) => s + (l._count || 0), allCount) }}</span>
    </div>

    <div
      v-for="list in todoLists"
      :key="list.id"
      :class="[
        'flex items-center px-1 py-1.5 rounded-lg cursor-pointer transition-colors',
        selectedListId === list.id ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
      ]"
      @click="$emit('select', list.id)"
    >
      <div class="w-3 h-3 rounded mr-2 shrink-0" :style="{ backgroundColor: list.color }" />
      <span class="text-xs flex-1 truncate">{{ list.name }}</span>
      <div class="flex items-center gap-1 ml-1">
        <button
          class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          @click.stop="openEditDialog(list)"
        >
          <i class="mdi mdi-pencil-outline text-xs text-gray-500" />
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
            <span class="text-base font-bold text-gray-900 dark:text-gray-100">New Task List</span>
            <div class="flex-1" />
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800" @click="addDialog = false">
              <i class="mdi mdi-close text-gray-700 dark:text-gray-300" />
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
            <span class="text-base font-bold text-gray-900 dark:text-gray-100">Edit Task List</span>
            <div class="flex-1" />
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800" @click="editDialog = false">
              <i class="mdi mdi-close text-gray-700 dark:text-gray-300" />
            </button>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="p-5 space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
              <input
                v-model="editForm.name"
                type="text"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
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
import { todoListsApi } from '../api/index.js'

const props = defineProps({
  todoLists: { type: Array, default: () => [] },
  selectedListId: { type: Number, default: null },
  allCount: { type: Number, default: 0 },
})

const emit = defineEmits(['update', 'select'])

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
const editForm = ref({ id: null, name: '', color: '#3b82f6' })

function openAddDialog() {
  addForm.value = { name: '', color: '#3b82f6' }
  addError.value = ''
  addDialog.value = true
}

function openEditDialog(list) {
  editForm.value = { id: list.id, name: list.name, color: list.color }
  editError.value = ''
  editDialog.value = true
}

async function saveAdd() {
  addError.value = ''
  if (!addForm.value.name) { addError.value = 'Name is required'; return }
  saving.value = true
  try {
    await todoListsApi.create(addForm.value)
    addDialog.value = false
    emit('update')
  } catch (err) {
    console.error('Failed to create todo list', err)
  } finally {
    saving.value = false
  }
}

async function saveEdit() {
  editError.value = ''
  if (!editForm.value.name) { editError.value = 'Name is required'; return }
  saving.value = true
  try {
    await todoListsApi.update(editForm.value.id, { name: editForm.value.name, color: editForm.value.color })
    editDialog.value = false
    emit('update')
  } catch (err) {
    console.error('Failed to update todo list', err)
  } finally {
    saving.value = false
  }
}

async function deleteList() {
  try {
    await todoListsApi.delete(editForm.value.id)
    editDialog.value = false
    emit('update', { deletedId: editForm.value.id })
  } catch (err) {
    console.error('Failed to delete todo list', err)
  }
}
</script>
