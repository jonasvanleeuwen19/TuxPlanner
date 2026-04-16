<template>
  <v-dialog :model-value="modelValue" max-width="600" @update:model-value="$emit('update:modelValue', $event)">
    <v-card rounded="xl" elevation="8">
      <v-card-title class="d-flex align-center pa-5 pb-3">
        <div class="event-dialog-icon mr-3">
          <v-icon :icon="isEdit ? 'mdi-calendar-edit' : 'mdi-calendar-plus'" color="primary" size="22" />
        </div>
        <span class="text-h6 font-weight-bold">{{ isEdit ? 'Edit Event' : 'New Event' }}</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" size="small" @click="close" />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-5">
        <v-form ref="formRef" @submit.prevent="submit">
          <v-text-field
            v-model="form.title"
            label="Title"
            prepend-inner-icon="mdi-format-title"
            variant="outlined"
            density="comfortable"
            :rules="[v => !!v || 'Title is required']"
            class="mb-3"
            autofocus
          />

          <div class="mb-3">
            <MarkdownEditor
              v-model="form.description"
              label="Description"
              placeholder="Add a description (Markdown supported)…"
              :rows="3"
            />
          </div>

          <v-text-field
            v-model="form.location"
            label="Location"
            prepend-inner-icon="mdi-map-marker-outline"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />

          <!-- Calendar List selector — exclude virtual TODO's list -->
          <v-select
            v-if="!isIcalEvent"
            v-model="form.calendar_list_id"
            :items="writableCalendarListItems"
            item-title="name"
            item-value="id"
            label="Calendar list"
            prepend-inner-icon="mdi-calendar-multiple"
            variant="outlined"
            density="comfortable"
            clearable
            class="mb-3"
          >
            <template #item="{ item, props: itemProps }">
              <v-list-item v-bind="itemProps">
                <template #prepend>
                  <div
                    class="list-color-dot mr-3"
                    :style="{ backgroundColor: item.raw.color }"
                  />
                </template>
              </v-list-item>
            </template>
            <template #selection="{ item }">
              <div class="d-flex align-center">
                <div class="list-color-dot mr-2" :style="{ backgroundColor: item.raw.color }" />
                {{ item.raw.name }}
              </div>
            </template>
          </v-select>

          <v-checkbox
            v-model="form.all_day"
            label="All day"
            color="primary"
            density="compact"
            class="mb-2"
          />

          <v-row dense>
            <v-col :cols="form.all_day ? 12 : 6">
              <v-text-field
                v-model="form.start"
                :label="form.all_day ? 'Date' : 'Start'"
                prepend-inner-icon="mdi-calendar"
                variant="outlined"
                density="comfortable"
                :type="form.all_day ? 'date' : 'datetime-local'"
                :rules="[v => !!v || 'Start is required']"
              />
            </v-col>
            <v-col v-if="!form.all_day" cols="6">
              <v-text-field
                v-model="form.end"
                label="End"
                prepend-inner-icon="mdi-calendar-end"
                variant="outlined"
                density="comfortable"
                type="datetime-local"
              />
            </v-col>
          </v-row>

          <div v-if="!isIcalEvent" class="d-flex align-center gap-2 mt-2">
            <span class="text-body-2 text-medium-emphasis mr-2">Color override</span>
            <div
              v-for="color in colors"
              :key="color"
              class="color-swatch"
              :style="{ backgroundColor: color }"
              :class="{ selected: form.color === color }"
              @click="form.color = form.color === color ? null : color"
            />
          </div>
        </v-form>

        <!-- Subtasks section (only for saved events) -->
        <template v-if="isEdit">
          <v-divider class="my-4" />
          <div class="d-flex align-center mb-3">
            <span class="text-body-1 font-weight-semibold">Subtasks</span>
            <v-spacer />
            <v-btn
              size="small"
              variant="tonal"
              color="primary"
              prepend-icon="mdi-plus"
              rounded="lg"
              @click="openAddSubtask"
            >
              Add
            </v-btn>
          </div>

          <div v-if="subtasksLoading" class="text-center py-2">
            <v-progress-circular indeterminate size="20" color="primary" />
          </div>

          <div v-else>
            <!-- Group subtasks by category -->
            <template v-for="(group, catName) in groupedSubtasks" :key="catName">
              <div class="text-caption text-medium-emphasis font-weight-semibold text-uppercase mb-1 mt-2">
                {{ catName }}
              </div>
              <div
                v-for="subtask in group"
                :key="subtask.id"
                class="subtask-item pa-2 rounded-lg mb-1"
              >
                <div class="d-flex align-center">
                  <v-checkbox
                    :model-value="subtask.completed"
                    density="compact"
                    hide-details
                    color="primary"
                    class="flex-shrink-0 mr-1"
                    style="max-width: 32px"
                    @update:model-value="toggleSubtask(subtask)"
                  />
                  <div class="flex-grow-1 min-w-0">
                    <span
                      class="text-body-2"
                      :class="{ 'text-decoration-line-through text-medium-emphasis': subtask.completed }"
                    >
                      {{ subtask.title }}
                    </span>
                    <div
                      v-if="subtask.description"
                      class="text-caption text-medium-emphasis mt-0.5"
                      style="white-space: pre-wrap"
                    >
                      {{ subtask.description }}
                    </div>
                  </div>
                  <v-btn
                    :icon="expandedSubtask === subtask.id ? 'mdi-chevron-up' : 'mdi-pencil-outline'"
                    size="x-small"
                    variant="text"
                    class="mr-1"
                    @click="toggleExpandSubtask(subtask)"
                  />
                  <v-btn
                    icon="mdi-close"
                    size="x-small"
                    variant="text"
                    @click="removeSubtask(subtask)"
                  />
                </div>
                <!-- Inline description editor -->
                <div v-if="expandedSubtask === subtask.id" class="mt-2">
                  <MarkdownEditor
                    v-model="subtask.description"
                    label="Subtask description"
                    placeholder="Add subtask notes (Markdown supported)…"
                    :rows="2"
                  />
                  <div class="d-flex gap-2 mt-1">
                    <v-btn size="x-small" color="primary" variant="tonal" rounded="lg" @click="saveSubtaskDescription(subtask)">Save</v-btn>
                    <v-btn size="x-small" variant="text" @click="expandedSubtask = null">Cancel</v-btn>
                  </div>
                </div>
              </div>
            </template>

            <div v-if="subtasks.length === 0" class="text-body-2 text-medium-emphasis py-1">
              No subtasks yet.
            </div>
          </div>

          <!-- Add subtask inline form -->
          <div v-if="addingSubtask" class="mt-2">
            <v-row dense>
              <v-col cols="12" sm="5">
                <v-select
                  v-model="newSubtask.category_id"
                  :items="categoryItems"
                  item-title="name"
                  item-value="id"
                  label="Category"
                  variant="outlined"
                  density="compact"
                  clearable
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="7">
                <v-text-field
                  v-model="newSubtask.title"
                  label="Subtask title"
                  variant="outlined"
                  density="compact"
                  hide-details
                  autofocus
                  @keyup.enter="saveSubtask"
                />
              </v-col>
            </v-row>
            <div class="mt-2">
              <MarkdownEditor
                v-model="newSubtask.description"
                label="Subtask description (optional)"
                placeholder="Add subtask notes (Markdown supported)…"
                :rows="2"
              />
            </div>
            <div class="d-flex gap-2 mt-2">
              <v-btn size="small" color="primary" variant="tonal" rounded="lg" @click="saveSubtask">Save</v-btn>
              <v-btn size="small" variant="text" @click="addingSubtask = false">Cancel</v-btn>
              <v-spacer />
              <v-btn
                size="small"
                variant="text"
                prepend-icon="mdi-tag-plus-outline"
                @click="manageCategoriesDialog = true"
              >
                Manage categories
              </v-btn>
            </div>
          </div>
        </template>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-btn
          v-if="isEdit && !isIcalEvent"
          color="error"
          variant="text"
          prepend-icon="mdi-trash-can"
          @click="$emit('delete', form.id)"
        >
          Delete
        </v-btn>
        <v-chip
          v-if="isIcalEvent"
          color="secondary"
          variant="tonal"
          size="small"
          prepend-icon="mdi-calendar-sync-outline"
        >
          iCal event
        </v-chip>
        <v-spacer />
        <v-btn variant="text" @click="close">Cancel</v-btn>
        <v-btn
          v-if="!isIcalEvent"
          color="primary"
          variant="elevated"
          rounded="lg"
          @click="submit"
        >
          {{ isEdit ? 'Save' : 'Create' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Manage Categories dialog -->
  <v-dialog v-model="manageCategoriesDialog" max-width="400">
    <v-card rounded="xl" elevation="8">
      <v-card-title class="d-flex align-center pa-5 pb-3">
        <span class="text-h6 font-weight-bold">Subtask Categories</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" size="small" @click="manageCategoriesDialog = false" />
      </v-card-title>
      <v-divider />
      <v-card-text class="pa-4">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="d-flex align-center pa-2 rounded-lg mb-1 subtask-item"
        >
          <v-icon icon="mdi-tag-outline" size="16" class="mr-2 text-medium-emphasis" />
          <span class="flex-grow-1 text-body-2">{{ cat.name }}</span>
          <v-btn
            icon="mdi-trash-can-outline"
            size="x-small"
            variant="text"
            color="error"
            @click="deleteCategory(cat)"
          />
        </div>
        <div v-if="categories.length === 0" class="text-body-2 text-medium-emphasis text-center py-2">
          No categories yet.
        </div>
        <div class="d-flex gap-2 mt-3">
          <v-text-field
            v-model="newCategoryName"
            label="New category name"
            variant="outlined"
            density="compact"
            hide-details
            @keyup.enter="addCategory"
          />
          <v-btn color="primary" variant="tonal" rounded="lg" @click="addCategory">Add</v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
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

const formRef = ref(null)
const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#0ea5e9']

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

// Filter out the virtual "TODO's" list from calendar list selector
const writableCalendarListItems = computed(() =>
  props.calendarLists.filter((l) => l.name !== "TODO's")
)

// Subtasks
const subtasks = ref([])
const subtasksLoading = ref(false)
const addingSubtask = ref(false)
const newSubtask = ref({ title: '', description: '', category_id: null })
const expandedSubtask = ref(null)

// Categories
const categories = ref([])
const manageCategoriesDialog = ref(false)
const newCategoryName = ref('')

const categoryItems = computed(() => categories.value)

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
      if (newEvent.id) {
        await fetchSubtasks(newEvent.id)
      }
    } else {
      form.value = defaultForm()
      subtasks.value = []
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

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
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

<style scoped>
.event-dialog-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(var(--v-theme-primary), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
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

.list-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.subtask-item {
  background: rgba(var(--v-theme-on-surface), 0.03);
}

.subtask-item:hover {
  background: rgba(var(--v-theme-on-surface), 0.06);
}

.font-weight-semibold {
  font-weight: 600;
}

.gap-2 {
  gap: 8px;
}
</style>
