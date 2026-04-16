<template>
  <v-dialog :model-value="modelValue" max-width="560" @update:model-value="$emit('update:modelValue', $event)">
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

          <v-textarea
            v-model="form.description"
            label="Description"
            prepend-inner-icon="mdi-text"
            variant="outlined"
            density="comfortable"
            rows="2"
            auto-grow
            class="mb-3"
          />

          <v-text-field
            v-model="form.location"
            label="Location"
            prepend-inner-icon="mdi-map-marker-outline"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />

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

          <div class="d-flex align-center gap-2 mt-2">
            <span class="text-body-2 text-medium-emphasis mr-2">Color</span>
            <div
              v-for="color in colors"
              :key="color"
              class="color-swatch"
              :style="{ backgroundColor: color }"
              :class="{ selected: form.color === color }"
              @click="form.color = color"
            />
          </div>
        </v-form>
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
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  event: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'save', 'delete'])

const formRef = ref(null)
const colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#0ea5e9']

const defaultForm = () => ({
  id: null,
  title: '',
  description: '',
  location: '',
  start: '',
  end: '',
  all_day: false,
  color: '#6366f1',
})

const form = ref(defaultForm())

const isEdit = computed(() => !!form.value.id)
const isIcalEvent = computed(() => form.value.source === 'ical')

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
        color: newEvent.color || '#6366f1',
        source: newEvent.source || null,
      }
    } else {
      form.value = defaultForm()
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

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  emit('save', {
    ...form.value,
    start: new Date(form.value.start).toISOString(),
    end: form.value.end ? new Date(form.value.end).toISOString() : null,
    location: form.value.location || null,
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
  background: rgba(99, 102, 241, 0.1);
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
</style>
