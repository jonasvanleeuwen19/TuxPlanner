<template>
  <v-dialog :model-value="modelValue" max-width="460" @update:model-value="$emit('update:modelValue', $event)">
    <v-card rounded="xl" elevation="8">
      <v-card-title class="d-flex align-center pa-5 pb-3">
        <div class="todo-dialog-icon mr-3">
          <v-icon icon="mdi-checkbox-marked-circle-plus-outline" color="primary" size="22" />
        </div>
        <span class="text-h6 font-weight-bold">New Task</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" size="small" @click="$emit('update:modelValue', false)" />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-5">
        <v-form ref="formRef" @submit.prevent="submit">
          <v-text-field
            v-model="form.title"
            label="Task title"
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

          <v-select
            v-model="form.priority"
            label="Priority"
            prepend-inner-icon="mdi-flag-outline"
            variant="outlined"
            density="comfortable"
            :items="priorityOptions"
            item-title="label"
            item-value="value"
            class="mb-3"
          />

          <v-text-field
            v-model="form.due_date"
            label="Due date"
            prepend-inner-icon="mdi-calendar-clock"
            variant="outlined"
            density="comfortable"
            type="datetime-local"
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="primary" variant="elevated" rounded="lg" @click="submit">Add Task</v-btn>
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

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const defaultForm = () => ({ title: '', description: '', priority: 'medium', due_date: '' })
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
    priority: form.value.priority,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
  })
}
</script>

<style scoped>
.todo-dialog-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
