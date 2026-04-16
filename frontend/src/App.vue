<template>
  <v-app :theme="theme" :class="theme">
    <v-app-bar
      color="surface"
      elevation="0"
      border="b"
      height="60"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <RouterLink to="/" class="logo-link">
        <span class="logo-text">TuxPlanner</span>
      </RouterLink>
      <v-spacer />
      <v-btn
        :icon="theme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        variant="text"
        @click="toggleTheme"
      />
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" :width="240" color="surface" border="r">
      <Sidebar />
    </v-navigation-drawer>

    <v-main class="bg-background">
      <RouterView />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const theme = ref(localStorage.getItem('theme') || 'light')

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('theme', theme.value)
}

const drawer = ref(true)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  font-family: 'Inter', 'Roboto', sans-serif !important;
}

.logo-link {
  text-decoration: none;
}

.logo-text {
  font-family: 'Inter', sans-serif !important;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: rgb(var(--v-theme-primary));
}

.dark .logo-text {
  color: rgb(var(--v-theme-primary));
}
</style>
