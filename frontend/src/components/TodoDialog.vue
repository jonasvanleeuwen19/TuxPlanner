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

          <!-- Link to event -->
          <div v-if="events && events.length">
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Link to event</label>
            <div class="relative">
              <i class="mdi mdi-calendar-link absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <select
                v-model="form.event_id"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                @change="onEventLinkChange"
              >
                <option :value="null">No event</option>
                <option v-for="ev in events" :key="ev.id" :value="ev.id">{{ ev.title }} ({{ formatEventDate(ev) }})</option>
              </select>
            </div>
          </div>

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
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Due date
              <span v-if="form.event_id" class="ml-1 text-gray-400 dark:text-gray-500 font-normal">(synced from linked event)</span>
            </label>
            <div class="relative">
              <i class="mdi mdi-calendar-clock absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.due_date"
                type="datetime-local"
                :disabled="!!form.event_id"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 disabled:opacity-60 disabled:cursor-not-allowed"
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
  events: { type: Array, default: () => [] },
  linkedEventId: { type: Number, default: null },
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
  event_id: props.linkedEventId ?? null,
})

function formFromTodo(todo) {
  return {
    title: todo.title || '',
    description: todo.description || '',
    priority: todo.priority || 'medium',
    due_date: todo.due_date ? new Date(todo.due_date).toISOString().slice(0, 16) : '',
    todo_list_id: todo.todo_list_id ?? null,
    category: todo.category || 'Default',
    event_id: todo.event_id ?? null,
  }
}

const form = ref(defaultForm())

function applyEventDueDate(eventId) {
  if (!eventId) return
  const ev = props.events.find((e) => e.id === eventId)
  if (ev) {
    const dateStr = ev.end || ev.start
    if (dateStr) {
      form.value.due_date = new Date(dateStr).toISOString().slice(0, 16)
    }
  }
}

function onEventLinkChange() {
  if (form.value.event_id) {
    applyEventDueDate(form.value.event_id)
  } else {
    form.value.due_date = ''
  }
}

function formatEventDate(ev) {
  if (!ev?.start) return ''
  return new Date(ev.start).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      if (props.editTodo) {
        form.value = formFromTodo(props.editTodo)
      } else {
        form.value = { ...defaultForm(), todo_list_id: props.defaultListId ?? null, event_id: props.linkedEventId ?? null }
        if (props.linkedEventId) {
          applyEventDueDate(props.linkedEventId)
        }
      }
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

watch(
  () => props.linkedEventId,
  (id) => {
    if (props.modelValue && !props.editTodo) {
      form.value.event_id = id ?? null
      if (id) applyEventDueDate(id)
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
    event_id: form.value.event_id ?? null,
  })
}
</script>

