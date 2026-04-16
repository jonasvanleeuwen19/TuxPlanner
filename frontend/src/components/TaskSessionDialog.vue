<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="$emit('update:modelValue', false)"
    >
      <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center p-5 pb-3">
          <div class="w-9 h-9 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mr-3 shrink-0">
            <i class="mdi mdi-calendar-clock text-lg text-purple-500 dark:text-purple-400" />
          </div>
          <span class="text-base font-bold text-gray-900 dark:text-gray-100">
            {{ editSession ? 'Edit Work Session' : 'Plan Work Session' }}
          </span>
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
          <!-- Start time -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Start *</label>
            <div class="relative">
              <i class="mdi mdi-clock-start absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.start"
                type="datetime-local"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400"
              />
            </div>
            <p v-if="startError" class="text-xs text-red-500 mt-1">{{ startError }}</p>
          </div>

          <!-- End time -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">End</label>
            <div class="relative">
              <i class="mdi mdi-clock-end absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.end"
                type="datetime-local"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400"
              />
            </div>
          </div>

          <!-- Note -->
          <div>
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Note</label>
            <div class="relative">
              <i class="mdi mdi-note-text-outline absolute left-3 top-2.5 text-gray-400 dark:text-gray-500 text-sm pointer-events-none" />
              <input
                v-model="form.note"
                type="text"
                placeholder="Optional note for this session"
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400"
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
            class="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors"
            @click="submit"
          >
            {{ editSession ? 'Save Changes' : 'Add Session' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  editSession: { type: Object, default: null },
  defaultStart: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'save'])

const startError = ref('')

const defaultForm = () => ({
  start: props.defaultStart || '',
  end: '',
  note: '',
})

function formFromSession(session) {
  return {
    start: session.start ? new Date(session.start).toISOString().slice(0, 16) : '',
    end: session.end ? new Date(session.end).toISOString().slice(0, 16) : '',
    note: session.note || '',
  }
}

const form = ref(defaultForm())

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      form.value = props.editSession ? formFromSession(props.editSession) : defaultForm()
      startError.value = ''
    }
  }
)

watch(
  () => props.editSession,
  (session) => {
    if (session && props.modelValue) {
      form.value = formFromSession(session)
    }
  }
)

function submit() {
  startError.value = ''
  if (!form.value.start) {
    startError.value = 'Start time is required'
    return
  }
  emit('save', {
    start: new Date(form.value.start).toISOString(),
    end: form.value.end ? new Date(form.value.end).toISOString() : null,
    note: form.value.note || null,
  })
}
</script>
