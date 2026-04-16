<template>
  <div>
    <!-- Header row -->
    <div class="d-flex align-center mb-2 px-1">
      <span class="text-body-2 font-weight-semibold">My Calendars</span>
      <v-spacer />
      <v-btn
        icon="mdi-plus"
        size="x-small"
        variant="text"
        color="primary"
        @click="openAddDialog"
      />
    </div>

    <!-- List items -->
    <div
      v-for="list in calendarLists"
      :key="list.id"
      class="cal-list-item d-flex align-center px-1 py-1 rounded-lg"
    >
      <div
        class="cal-list-color mr-2 flex-shrink-0"
        :style="{ backgroundColor: list.color }"
      />
      <span class="text-body-2 flex-grow-1 text-truncate">{{ list.name }}</span>
      <div class="d-flex align-center gap-1">
        <v-btn
          icon="mdi-pencil-outline"
          size="x-small"
          variant="text"
          @click="openEditDialog(list)"
        />
        <v-switch
          :model-value="list.is_visible"
          density="compact"
          hide-details
          color="primary"
          class="flex-shrink-0"
          style="max-width: 44px"
          @update:model-value="toggleVisibility(list)"
        />
      </div>
    </div>

    <!-- Add Calendar List dialog -->
    <v-dialog v-model="addDialog" max-width="400">
      <v-card rounded="xl" elevation="8">
        <v-card-title class="d-flex align-center pa-5 pb-3">
          <span class="text-h6 font-weight-bold">New Calendar List</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="addDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-5">
          <v-form ref="addFormRef">
            <v-text-field
              v-model="addForm.name"
              label="Name"
              variant="outlined"
              density="comfortable"
              :rules="[v => !!v || 'Name is required']"
              class="mb-3"
              autofocus
            />
            <div class="text-body-2 text-medium-emphasis mb-2">Color</div>
            <div class="d-flex flex-wrap gap-2">
              <div
                v-for="color in colorOptions"
                :key="color"
                class="color-swatch"
                :style="{ backgroundColor: color }"
                :class="{ selected: addForm.color === color }"
                @click="addForm.color = color"
              />
            </div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="addDialog = false">Cancel</v-btn>
          <v-btn color="primary" variant="elevated" rounded="lg" :loading="saving" @click="saveAdd">
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Edit Calendar List dialog -->
    <v-dialog v-model="editDialog" max-width="400">
      <v-card rounded="xl" elevation="8">
        <v-card-title class="d-flex align-center pa-5 pb-3">
          <span class="text-h6 font-weight-bold">Edit Calendar List</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="editDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text class="pa-5">
          <v-form ref="editFormRef">
            <v-text-field
              v-model="editForm.name"
              label="Name"
              variant="outlined"
              density="comfortable"
              :rules="[v => !!v || 'Name is required']"
              :disabled="!!editForm.ical_feed_id"
              :hint="editForm.ical_feed_id ? 'Name is managed by ICAL feed' : ''"
              persistent-hint
              class="mb-3"
            />
            <div class="text-body-2 text-medium-emphasis mb-2">Color</div>
            <div class="d-flex flex-wrap gap-2">
              <div
                v-for="color in colorOptions"
                :key="color"
                class="color-swatch"
                :style="{ backgroundColor: color }"
                :class="{ selected: editForm.color === color }"
                @click="editForm.color = color"
              />
            </div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions class="pa-4">
          <v-btn
            v-if="!editForm.ical_feed_id"
            color="error"
            variant="text"
            prepend-icon="mdi-trash-can"
            @click="deleteList"
          />
          <v-spacer />
          <v-btn variant="text" @click="editDialog = false">Cancel</v-btn>
          <v-btn color="primary" variant="elevated" rounded="lg" :loading="saving" @click="saveEdit">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { calendarListsApi } from '../api/index.js'

const props = defineProps({
  calendarLists: { type: Array, default: () => [] },
})

const emit = defineEmits(['update'])

const colorOptions = [
  '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#ef4444', '#ec4899', '#0ea5e9',
  '#84cc16', '#f97316', '#64748b', '#a855f7',
]

const addDialog = ref(false)
const editDialog = ref(false)
const saving = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)

const addForm = ref({ name: '', color: '#3b82f6' })
const editForm = ref({ id: null, name: '', color: '#3b82f6', ical_feed_id: null })

function openAddDialog() {
  addForm.value = { name: '', color: '#3b82f6' }
  addDialog.value = true
}

function openEditDialog(list) {
  editForm.value = { id: list.id, name: list.name, color: list.color, ical_feed_id: list.ical_feed_id }
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
  const { valid } = await addFormRef.value.validate()
  if (!valid) return
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
  const { valid } = await editFormRef.value.validate()
  if (!valid) return
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

<style scoped>
.cal-list-item:hover {
  background: rgba(var(--v-theme-on-surface), 0.04);
}

.cal-list-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.color-swatch {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.15s;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.color-swatch:hover {
  transform: scale(1.2);
}

.color-swatch.selected {
  border-color: rgba(0, 0, 0, 0.4);
  transform: scale(1.15);
}

.font-weight-semibold {
  font-weight: 600;
}

.gap-1 {
  gap: 4px;
}

.gap-2 {
  gap: 8px;
}
</style>
