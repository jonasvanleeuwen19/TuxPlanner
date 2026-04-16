<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="px-4 pt-5 pb-3">
      <TodayPanel />
    </div>
    <hr class="border-gray-200 dark:border-gray-800" />
    <nav class="px-2 pt-3 flex flex-col gap-1">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 no-underline"
        active-class="bg-blue-50 dark:bg-gray-700 text-blue-600 dark:text-blue-400"
      >
        <i :class="['mdi text-lg', item.icon]" />
        {{ item.title }}
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import TodayPanel from './TodayPanel.vue'

const navItems = [
  { to: '/', icon: 'mdi-calendar-month', title: 'Calendar' },
  { to: '/todos', icon: 'mdi-checkbox-marked-circle-outline', title: 'Tasks' },
  { to: '/ical', icon: 'mdi-calendar-sync-outline', title: 'ICAL Sync' },
]
</script>
