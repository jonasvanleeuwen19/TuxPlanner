<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="$emit('update:modelValue', false)"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3">
          <div class="w-9 h-9 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-3 shrink-0">
            <i :class="['mdi text-lg text-blue-500 dark:text-blue-400', editTodo ? 'mdi-pencil-outline' : 'mdi-checkbox-marked-circle-plus-outline']" />
          </div>
          <span class="text-base font-bold text-gray-900 dark:text-gray-100">{{ editTodo ? 'Edit Task' : 'New Task' }}</span>
          <div class="flex-1" />
          <button
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            <i class="mdi mdi-close text-lg" />
          </button>
        </div>
        <hr class="border-gray-200 dark:border-gray-700" />

        <!-- Body -->
        <div class="p-5 space-y-4">
          <!-- Title -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Task title *</label>
            <div class="relative">
              <i class="mdi mdi-format-title absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.title"
                type="text"
                autofocus
                placeholder="Task title"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>
            <p v-if="titleError" class="text-xs text-red-500 mt-1">{{ titleError }}</p>
          </div>

          <!-- Description -->
          <MarkdownEditor
            v-model="form.description"
            label="Description"
            placeholder="Add a description (Markdown supported)…"
            :rows="3"
          />

          <!-- List selector -->
          <div v-if="todoLists && todoLists.length">
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">List</label>
            <div class="relative">
              <i class="mdi mdi-view-list absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <select
                v-model="form.todo_list_id"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              >
                <option :value="null">No list</option>
                <option v-for="list in todoLists" :key="list.id" :value="list.id">{{ list.name }}</option>
              </select>
            </div>
          </div>

          <!-- Priority -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
            <div class="relative">
              <i class="mdi mdi-flag-outline absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <select
                v-model="form.priority"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <!-- Category -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Category *</label>
            <div class="relative">
              <i class="mdi mdi-folder-outline absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.category"
                type="text"
                list="category-suggestions"
                placeholder="Default"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
              <datalist id="category-suggestions">
                <option v-for="cat in existingCategories" :key="cat" :value="cat" />
              </datalist>
            </div>
            <p v-if="categoryError" class="text-xs text-red-500 mt-1">{{ categoryError }}</p>
          </div>

          <!-- Due date -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Due date</label>
            <div class="relative">
              <i class="mdi mdi-calendar-clock absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.due_date"
                type="datetime-local"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>
          </div>
        </div>

        <hr class="border-gray-200 dark:border-gray-700" />

        <!-- Actions -->
        <div class="flex justify-end gap-2 p-4">
          <button
            class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            Cancel
          </button>
          <button
            class="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            @click="submit"
          >
            {{ editTodo ? 'Save Changes' : 'Add Task' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import MarkdownEditor from './MarkdownEditor.vue'

const props = defineProps({
  modelValue: Boolean,
  todoLists: { type: Array, default: () => [] },
  defaultListId: { type: Number, default: null },
  existingTodos: { type: Array, default: () => [] },
  editTodo: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'save'])

const titleError = ref('')
const categoryError = ref('')

const existingCategories = computed(() => {
  const cats = new Set(['Default'])
  for (const t of props.existingTodos) {
    if (t.category) cats.add(t.category)
  }
  return [...cats].sort()
})

const defaultForm = () => ({
  title: '',
  description: '',
  priority: 'medium',
  due_date: '',
  todo_list_id: props.defaultListId ?? null,
  category: 'Default',
})

function formFromTodo(todo) {
  return {
    title: todo.title || '',
    description: todo.description || '',
    priority: todo.priority || 'medium',
    due_date: todo.due_date ? new Date(todo.due_date).toISOString().slice(0, 16) : '',
    todo_list_id: todo.todo_list_id ?? null,
    category: todo.category || 'Default',
  }
}

const form = ref(defaultForm())

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      form.value = props.editTodo ? formFromTodo(props.editTodo) : { ...defaultForm(), todo_list_id: props.defaultListId ?? null }
      titleError.value = ''
      categoryError.value = ''
    }
  }
)

watch(
  () => props.editTodo,
  (todo) => {
    if (todo && props.modelValue) {
      form.value = formFromTodo(todo)
    }
  }
)

function submit() {
  titleError.value = ''
  categoryError.value = ''
  if (!form.value.title.trim()) {
    titleError.value = 'Title is required'
    return
  }
  if (!form.value.category.trim()) {
    categoryError.value = 'Category is required'
    return
  }
  emit('save', {
    title: form.value.title,
    description: form.value.description || null,
    priority: form.value.priority,
    due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
    todo_list_id: form.value.todo_list_id ?? null,
    category: form.value.category.trim() || 'Default',
  })
}
</script>
