<template>
  <div class="sidebar d-flex flex-column" style="height: 100%">
    <div class="px-4 pt-5 pb-3">
      <TodayPanel />
    </div>

    <v-divider />

    <v-list nav density="compact" class="px-2 pt-3">
      <v-list-item
        prepend-icon="mdi-calendar-month"
        title="Calendar"
        to="/"
        rounded="lg"
        active-color="primary"
        class="mb-1"
      />
      <v-list-item
        prepend-icon="mdi-checkbox-marked-circle-outline"
        title="Tasks"
        to="/todos"
        rounded="lg"
        active-color="primary"
        class="mb-1"
      />
      <v-list-item
        prepend-icon="mdi-calendar-sync-outline"
        title="ICAL Sync"
        to="/ical"
        rounded="lg"
        active-color="primary"
        class="mb-1"
      />
    </v-list>
  </div>
</template>

<script setup>
import TodayPanel from './TodayPanel.vue'
</script>

<style scoped>
.sidebar {
  overflow: hidden;
}
</style>
