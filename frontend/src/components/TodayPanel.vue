<template>
  <div>
    <div class="flex items-center mb-3">
      <i class="mdi mdi-calendar-today text-blue-500 mr-2 text-base" />
      <span class="text-xs font-semibold uppercase tracking-widest text-gray-500 dark:text-gray-400">Today</span>
    </div>

    <div class="text-center py-3 mb-3 rounded-2xl bg-blue-50 dark:bg-gray-800">
      <div class="text-4xl font-bold text-blue-500 dark:text-blue-400">{{ dayNumber }}</div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ fullDate }}</div>
    </div>

    <div class="grid grid-cols-2 gap-2">
      <div class="bg-blue-50 dark:bg-gray-800 rounded-xl p-2 text-center">
        <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ weekNumber }}</div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Week</div>
      </div>
      <div class="bg-purple-50 dark:bg-gray-800 rounded-xl p-2 text-center">
        <div class="text-lg font-bold text-purple-600 dark:text-purple-400">{{ dayOfYear }}</div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Day of year</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const now = computed(() => new Date())
const dayNumber = computed(() => now.value.getDate())
const fullDate = computed(() =>
  now.value.toLocaleDateString('en-US', { weekday: 'long', month: 'long', year: 'numeric' })
)
const weekNumber = computed(() => {
  const d = new Date(Date.UTC(now.value.getFullYear(), now.value.getMonth(), now.value.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7)
})
const dayOfYear = computed(() => {
  const start = new Date(now.value.getFullYear(), 0, 0)
  return Math.floor((now.value - start) / (1000 * 60 * 60 * 24))
})
</script>
