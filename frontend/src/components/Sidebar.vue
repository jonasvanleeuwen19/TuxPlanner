<template>
  <div class="sidebar d-flex flex-column" style="height: 100%">
    <!-- App Info -->
    <v-list-item class="py-4">
      <template #prepend>
        <v-avatar color="primary" size="40">
          <v-icon icon="mdi-penguin" color="white" />
        </v-avatar>
      </template>
      <v-list-item-title class="text-h6 font-weight-bold">TuxPlanner</v-list-item-title>
      <v-list-item-subtitle>Jouw persoonlijke planner</v-list-item-subtitle>
    </v-list-item>

    <v-divider />

    <!-- Today Section -->
    <TodayPanel />

    <v-divider />

    <!-- Todo Section -->
    <div class="flex-grow-1 overflow-auto">
      <div class="d-flex align-center px-4 pt-3 pb-1">
        <v-icon icon="mdi-checkbox-marked-circle-outline" color="primary" class="mr-2" />
        <span class="text-subtitle-1 font-weight-medium">Todo's</span>
        <v-spacer />
        <v-btn
          icon="mdi-plus"
          size="small"
          variant="text"
          color="primary"
          @click="$emit('add-todo')"
        />
      </div>

      <v-progress-linear v-if="loadingTodos" indeterminate color="primary" />

      <v-list v-else density="compact" class="px-2">
        <v-list-item
          v-for="todo in todos"
          :key="todo.id"
          :class="{ 'text-decoration-line-through text-medium-emphasis': todo.completed }"
          rounded="lg"
          class="mb-1"
        >
          <template #prepend>
            <v-checkbox-btn
              :model-value="todo.completed"
              color="primary"
              @update:model-value="$emit('toggle-todo', todo)"
            />
          </template>
          <v-list-item-title class="text-body-2">{{ todo.title }}</v-list-item-title>
          <v-list-item-subtitle v-if="todo.due_date" class="text-caption">
            <v-icon icon="mdi-clock-outline" size="10" class="mr-1" />
            {{ formatDate(todo.due_date) }}
          </v-list-item-subtitle>
          <template #append>
            <v-btn
              icon="mdi-trash-can-outline"
              size="x-small"
              variant="text"
              color="error"
              @click="$emit('delete-todo', todo.id)"
            />
          </template>
        </v-list-item>

        <v-list-item v-if="todos.length === 0">
          <v-list-item-title class="text-caption text-medium-emphasis text-center py-2">
            Geen todo's. Voeg er een toe!
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </div>
  </div>
</template>

<script setup>
import TodayPanel from './TodayPanel.vue'

defineProps({
  todos: { type: Array, default: () => [] },
  loadingTodos: { type: Boolean, default: false },
})

defineEmits(['add-todo', 'toggle-todo', 'delete-todo'])

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })
}
</script>

<style scoped>
.sidebar {
  overflow: hidden;
}
</style>
