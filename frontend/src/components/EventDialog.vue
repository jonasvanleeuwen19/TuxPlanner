<template>
  <v-dialog :model-value="modelValue" max-width="520" @update:model-value="$emit('update:modelValue', $event)">
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center pa-4">
        <v-icon :icon="isEdit ? 'mdi-calendar-edit' : 'mdi-calendar-plus'" color="primary" class="mr-2" />
        {{ isEdit ? 'Afspraak bewerken' : 'Nieuwe afspraak' }}
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" @click="close" />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <v-form ref="formRef" @submit.prevent="submit">
          <v-text-field
            v-model="form.title"
            label="Titel"
            prepend-inner-icon="mdi-format-title"
            variant="outlined"
            density="compact"
            :rules="[v => !!v || 'Titel is verplicht']"
            class="mb-3"
          />

          <v-textarea
            v-model="form.description"
            label="Beschrijving (optioneel)"
            prepend-inner-icon="mdi-text"
            variant="outlined"
            density="compact"
            rows="2"
            class="mb-3"
          />

          <v-checkbox
            v-model="form.all_day"
            label="Hele dag"
            color="primary"
            density="compact"
            class="mb-2"
          />

          <v-text-field
            v-model="form.start"
            :label="form.all_day ? 'Datum' : 'Start'"
            prepend-inner-icon="mdi-calendar"
            variant="outlined"
            density="compact"
            :type="form.all_day ? 'date' : 'datetime-local'"
            :rules="[v => !!v || 'Start is verplicht']"
            class="mb-3"
          />

          <v-text-field
            v-if="!form.all_day"
            v-model="form.end"
            label="Einde (optioneel)"
            prepend-inner-icon="mdi-calendar-end"
            variant="outlined"
            density="compact"
            type="datetime-local"
            class="mb-3"
          />

          <div class="d-flex align-center gap-2 mb-1">
            <span class="text-body-2 text-medium-emphasis">Kleur</span>
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
          v-if="isEdit"
          color="error"
          variant="text"
          prepend-icon="mdi-trash-can"
          @click="$emit('delete', form.id)"
        >
          Verwijderen
        </v-btn>
        <v-spacer />
        <v-btn variant="text" @click="close">Annuleren</v-btn>
        <v-btn color="primary" variant="elevated" @click="submit">
          {{ isEdit ? 'Opslaan' : 'Toevoegen' }}
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
const colors = ['#1565C0', '#2E7D32', '#C62828', '#F57F17', '#6A1B9A', '#00838F', '#AD1457']

const defaultForm = () => ({
  id: null,
  title: '',
  description: '',
  start: '',
  end: '',
  all_day: false,
  color: '#1565C0',
})

const form = ref(defaultForm())

const isEdit = computed(() => !!form.value.id)

watch(
  () => props.event,
  (newEvent) => {
    if (newEvent) {
      form.value = {
        id: newEvent.id || null,
        title: newEvent.title || '',
        description: newEvent.description || '',
        start: formatForInput(newEvent.start, newEvent.all_day),
        end: newEvent.end ? formatForInput(newEvent.end, newEvent.all_day) : '',
        all_day: newEvent.all_day || false,
        color: newEvent.color || '#1565C0',
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
  // datetime-local format: YYYY-MM-DDTHH:MM
  return d.toISOString().slice(0, 16)
}

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  emit('save', {
    ...form.value,
    start: new Date(form.value.start).toISOString(),
    end: form.value.end ? new Date(form.value.end).toISOString() : null,
  })
}

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.15s;
  border: 2px solid transparent;
}
.color-swatch:hover {
  transform: scale(1.2);
}
.color-swatch.selected {
  border-color: #000;
  transform: scale(1.15);
}
</style>
