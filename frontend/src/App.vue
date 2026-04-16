<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <!-- Top bar -->
    <header class="fixed top-0 left-0 right-0 z-30 h-14 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center px-3 gap-3">
      <button
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        @click="drawer = !drawer"
      >
        <i class="mdi mdi-menu text-xl" />
      </button>
      <RouterLink to="/" class="no-underline">
        <span class="text-lg font-bold tracking-tight text-blue-500 dark:text-blue-400">TuxPlanner</span>
      </RouterLink>
      <div class="flex-1" />
      <button
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        @click="toggleTheme"
      >
        <i :class="['mdi text-xl', theme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night']" />
      </button>
    </header>

    <!-- Body -->
    <div class="flex pt-14 min-h-screen">
      <!-- Sidebar drawer -->
      <aside
        :class="[
          'fixed left-0 top-14 bottom-0 z-20 w-60 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-transform duration-300',
          drawer ? 'translate-x-0' : '-translate-x-full'
        ]"
      >
        <Sidebar />
      </aside>

      <!-- Main content -->
      <main
        :class="[
          'flex-1 transition-all duration-300 min-w-0',
          drawer ? 'ml-60' : 'ml-0'
        ]"
      >
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const theme = ref(localStorage.getItem('theme') || 'light')

function applyTheme(val) {
  document.documentElement.classList.toggle('dark', val === 'dark')
}

watch(theme, applyTheme, { immediate: true })

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('theme', theme.value)
}

const drawer = ref(true)
</script>
