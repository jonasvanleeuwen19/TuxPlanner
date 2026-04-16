<template>
  <div class="today-panel">
    <div class="d-flex align-center mb-3">
      <v-icon icon="mdi-calendar-today" color="primary" class="mr-2" size="18" />
      <span class="text-caption font-weight-semibold text-uppercase text-medium-emphasis letter-spacing-wide">Today</span>
    </div>

    <div class="today-date text-center py-3 mb-3">
      <div class="text-h2 font-weight-bold text-primary">{{ dayNumber }}</div>
      <div class="text-body-2 text-medium-emphasis mt-1">{{ fullDate }}</div>
    </div>

    <v-row dense>
      <v-col cols="6">
        <v-card variant="tonal" color="primary" rounded="xl" class="pa-2 text-center">
          <div class="text-h6 font-weight-bold">{{ weekNumber }}</div>
          <div class="text-caption text-medium-emphasis">Week</div>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card variant="tonal" color="secondary" rounded="xl" class="pa-2 text-center">
          <div class="text-h6 font-weight-bold">{{ dayOfYear }}</div>
          <div class="text-caption text-medium-emphasis">Day of year</div>
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
  now.value.toLocaleDateString('en-US', {
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
  border-radius: 16px;
  background: rgba(99, 102, 241, 0.06);
}

.letter-spacing-wide {
  letter-spacing: 0.08em;
}
</style>
