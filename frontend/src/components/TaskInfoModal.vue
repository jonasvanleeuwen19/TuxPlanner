<template>
  <Teleport to="body">
    <div
      v-if="modelValue && todo"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60"
      @click.self="close"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3 shrink-0">
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <input
              type="checkbox"
              :checked="todo.completed"
              class="w-4 h-4 accent-blue-500 cursor-pointer shrink-0"
              @change="$emit('toggle', todo)"
            />
            <span
              :class="[
                'text-base font-bold truncate',
                todo.completed ? 'line-through text-gray-400 dark:text-gray-600' : 'text-gray-900 dark:text-gray-100'
              ]"
            >{{ todo.title }}</span>
          </div>
          <button
            class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors ml-2 shrink-0"
            @click="close"
          >
            <i class="mdi mdi-close text-lg" />
          </button>
        </div>
        <hr class="border-gray-200 dark:border-gray-700 shrink-0" />

        <!-- Body -->
        <div class="overflow-y-auto flex-1 p-5 space-y-4">
          <!-- Meta -->
          <div class="flex flex-wrap gap-2">
            <span
              v-if="todo.priority"
              :class="['text-xs px-2 py-0.5 rounded-md font-medium', priorityClass(todo.priority)]"
            >
              {{ todo.priority }}
            </span>
            <span
              v-if="todo.due_date"
              class="text-xs px-2 py-0.5 rounded-md font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center gap-1"
            >
              <i class="mdi mdi-clock-outline text-xs" />
              Due {{ formatDateTime(todo.due_date) }}
            </span>
          </div>

          <!-- Description -->
          <div v-if="todo.description" class="flex items-start gap-2">
            <i class="mdi mdi-text-box-outline text-sm text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" />
            <div
              class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm max-w-none dark:prose-invert flex-1"
              v-html="renderedDescription"
            />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  modelValue: Boolean,
  todo: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'toggle'])

const renderedDescription = computed(() => {
  if (!props.todo?.description) return ''
  return DOMPurify.sanitize(marked.parse(props.todo.description))
})

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function priorityClass(priority) {
  if (priority === 'high') return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
  if (priority === 'medium') return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
  return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
}

function close() {
  emit('update:modelValue', false)
}
</script>
