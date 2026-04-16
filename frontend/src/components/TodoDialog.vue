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

          <div class="mb-3">
            <MarkdownEditor
              v-model="form.description"
              label="Description"
              placeholder="Add a description (Markdown supported)…"
              :rows="3"
            />
          </div>

          <v-select
            v-if="todoLists && todoLists.length"
            v-model="form.todo_list_id"
            :items="todoListItems"
            item-title="name"
            item-value="id"
            label="List"
            prepend-inner-icon="mdi-view-list"
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
import { ref, computed, watch } from 'vue'
import MarkdownEditor from './MarkdownEditor.vue'

const props = defineProps({
  modelValue: Boolean,
  todoLists: { type: Array, default: () => [] },
  defaultListId: { type: Number, default: null },
})

const emit = defineEmits(['update:modelValue', 'save'])

const formRef = ref(null)

const todoListItems = computed(() => props.todoLists)

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const defaultForm = () => ({
  title: '',
  description: '',
  priority: 'medium',
  due_date: '',
  todo_list_id: props.defaultListId ?? null,
})
const form = ref(defaultForm())

watch(
  () => props.modelValue,
  (val) => {
    if (val) form.value = { ...defaultForm(), todo_list_id: props.defaultListId ?? null }
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
    todo_list_id: form.value.todo_list_id ?? null,
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

.list-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}
</style>
