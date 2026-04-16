<template>
  <v-dialog :model-value="modelValue" max-width="420" @update:model-value="$emit('update:modelValue', $event)">
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center pa-4">
        <v-icon icon="mdi-checkbox-marked-circle-plus-outline" color="primary" class="mr-2" />
        Nieuwe todo
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)" />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <v-form ref="formRef" @submit.prevent="submit">
          <v-text-field
            v-model="form.title"
            label="Todo titel"
            prepend-inner-icon="mdi-format-title"
            variant="outlined"
            density="compact"
            :rules="[v => !!v || 'Titel is verplicht']"
            class="mb-3"
            autofocus
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

          <v-text-field
            v-model="form.due_date"
            label="Deadline (optioneel)"
            prepend-inner-icon="mdi-calendar-clock"
            variant="outlined"
            density="compact"
            type="datetime-local"
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Annuleren</v-btn>
        <v-btn color="primary" variant="elevated" @click="submit">Toevoegen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
})

const emit = defineEmits(['update:modelValue', 'save'])

const formRef = ref(null)

const defaultForm = () => ({ title: '', description: '', due_date: '' })
const form = ref(defaultForm())

watch(
  () => props.modelValue,
  (val) => {
    if (val) form.value = defaultForm()
  }
)

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  emit('save', {
    title: form.value.title,
    description: form.value.description || null,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
  })
}
</script>
