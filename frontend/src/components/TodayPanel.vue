<template>
  <div class="today-panel px-4 py-3">
    <div class="d-flex align-center mb-2">
      <v-icon icon="mdi-calendar-today" color="primary" class="mr-2" />
      <span class="text-subtitle-1 font-weight-medium">Vandaag</span>
    </div>

    <!-- Date display -->
    <div class="today-date text-center py-3">
      <div class="text-h2 font-weight-bold text-primary">{{ dayNumber }}</div>
      <div class="text-subtitle-1 text-medium-emphasis">{{ fullDate }}</div>
    </div>

    <!-- Quick stats -->
    <v-row dense class="mt-1">
      <v-col cols="6">
        <v-card variant="tonal" color="primary" rounded="lg" class="pa-2 text-center">
          <div class="text-h6 font-weight-bold">{{ weekNumber }}</div>
          <div class="text-caption">Week</div>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card variant="tonal" color="secondary" rounded="lg" class="pa-2 text-center">
          <div class="text-h6 font-weight-bold">{{ dayOfYear }}</div>
          <div class="text-caption">Dag v/h jaar</div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const now = computed(() => new Date())

const dayNumber = computed(() => now.value.getDate())

const fullDate = computed(() =>
  now.value.toLocaleDateString('nl-NL', {
    weekday: 'long',
    month: 'long',
    year: 'numeric',
  })
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
  const diff = now.value - start
  return Math.floor(diff / (1000 * 60 * 60 * 24))
})
</script>

<style scoped>
.today-panel {
  background: transparent;
}

.today-date {
  border-radius: 12px;
  background: rgba(21, 101, 192, 0.05);
}
</style>
