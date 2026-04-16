<template>
  <v-container fluid class="pa-4 pa-md-6">
    <div class="d-flex align-center mb-6">
      <div>
        <div class="text-h5 font-weight-bold">ICAL Sync</div>
        <div class="text-body-2 text-medium-emphasis">Automatically syncs every hour</div>
      </div>
      <v-spacer />
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        rounded="lg"
        elevation="0"
        @click="addDialog = true"
      >
        Add Feed
      </v-btn>
    </div>

    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" rounded />

    <div v-if="feeds.length === 0 && !loading" class="text-center py-16">
      <v-icon icon="mdi-calendar-sync-outline" size="64" color="primary" opacity="0.3" class="mb-4" />
      <div class="text-h6 text-medium-emphasis font-weight-medium">No ICAL feeds added</div>
      <div class="text-body-2 text-disabled mt-1">Add an ICAL URL to sync external calendars</div>
      <v-btn
        color="primary"
        variant="tonal"
        rounded="lg"
        prepend-icon="mdi-plus"
        class="mt-4"
        @click="addDialog = true"
      >
        Add your first feed
      </v-btn>
    </div>

    <v-row>
      <v-col
        v-for="feed in feeds"
        :key="feed.id"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card rounded="xl" elevation="0" border>
          <v-card-text class="pa-4">
            <div class="d-flex align-start justify-space-between mb-3">
              <div
                class="feed-icon mr-3 flex-shrink-0"
                :style="{ background: `${getListColor(feed)}22` }"
              >
                <v-icon icon="mdi-calendar-sync-outline" :color="getListColor(feed)" size="22" />
              </div>
              <div class="flex-grow-1 min-width-0">
                <div class="text-body-1 font-weight-semibold">{{ feed.name }}</div>
                <div class="text-caption text-medium-emphasis text-truncate mt-1">{{ feed.url }}</div>
              </div>
              <v-chip
                :color="feed.is_active ? 'success' : 'default'"
                variant="tonal"
                size="x-small"
                rounded="lg"
                class="ml-2 flex-shrink-0"
              >
                {{ feed.is_active ? 'Active' : 'Paused' }}
              </v-chip>
            </div>

            <div class="text-caption text-medium-emphasis mb-3">
              <v-icon icon="mdi-clock-sync-outline" size="14" class="mr-1" />
              {{ feed.last_synced ? `Last synced ${formatDateTime(feed.last_synced)}` : 'Never synced' }}
            </div>

            <!-- Color picker for the linked calendar list -->
            <div class="d-flex align-center mb-3 flex-wrap gap-1">
              <span class="text-caption text-medium-emphasis mr-1">Color:</span>
              <div
                v-for="color in colorOptions"
                :key="color"
                class="color-swatch"
                :style="{ backgroundColor: color }"
                :class="{ selected: getListColor(feed) === color }"
                @click="updateFeedColor(feed, color)"
              />
            </div>

            <div class="d-flex gap-2">
              <v-btn
                size="small"
                variant="tonal"
                color="primary"
                rounded="lg"
                prepend-icon="mdi-refresh"
                :loading="syncingId === feed.id"
                @click="syncFeed(feed)"
              >
                Sync now
              </v-btn>
              <v-btn
                size="small"
                variant="tonal"
                :color="feed.is_active ? 'warning' : 'success'"
                rounded="lg"
                :prepend-icon="feed.is_active ? 'mdi-pause' : 'mdi-play'"
                @click="toggleActive(feed)"
              >
                {{ feed.is_active ? 'Pause' : 'Resume' }}
              </v-btn>
              <v-spacer />
              <v-btn
                icon="mdi-trash-can-outline"
                size="small"
                variant="text"
                color="error"
                @click="confirmDelete(feed)"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="addDialog" max-width="480">
      <v-card rounded="xl" elevation="8">
        <v-card-title class="d-flex align-center pa-5 pb-3">
          <div class="feed-icon mr-3">
            <v-icon icon="mdi-calendar-plus" color="primary" size="22" />
          </div>
          <span class="text-h6 font-weight-bold">Add ICAL Feed</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="addDialog = false" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-5">
          <v-form ref="addFormRef">
            <v-text-field
              v-model="newFeed.name"
              label="Feed name"
              prepend-inner-icon="mdi-label-outline"
              variant="outlined"
              density="comfortable"
              :rules="[v => !!v || 'Name is required']"
              class="mb-3"
              autofocus
            />
            <v-text-field
              v-model="newFeed.url"
              label="ICAL URL (.ics)"
              prepend-inner-icon="mdi-link"
              variant="outlined"
              density="comfortable"
              :rules="[v => !!v || 'URL is required', v => /^(https?|webcals?):\/\//.test(v) || 'Must be a valid URL']"
              hint="Paste your calendar's .ics subscribe link"
              persistent-hint
              class="mb-3"
            />
            <div class="text-body-2 text-medium-emphasis mb-2">Calendar color</div>
            <div class="d-flex flex-wrap gap-2">
              <div
                v-for="color in colorOptions"
                :key="color"
                class="color-swatch"
                :style="{ backgroundColor: color }"
                :class="{ selected: newFeed.color === color }"
                @click="newFeed.color = color"
              />
            </div>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="addDialog = false">Cancel</v-btn>
          <v-btn color="primary" variant="elevated" rounded="lg" :loading="adding" @click="addFeed">
            Add & Sync
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card rounded="xl">
        <v-card-title class="pa-5 pb-3 text-h6 font-weight-bold">Remove Feed</v-card-title>
        <v-card-text class="px-5 pb-2">
          Remove <strong>{{ feedToDelete?.name }}</strong>? All imported events from this feed will be deleted.
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="elevated" rounded="lg" @click="deleteFeed">Remove</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { icalApi, calendarListsApi } from '../api/index.js'

const feeds = ref([])
const calendarLists = ref([])
const loading = ref(false)
const addDialog = ref(false)
const deleteDialog = ref(false)
const feedToDelete = ref(null)
const addFormRef = ref(null)
const adding = ref(false)
const syncingId = ref(null)

const colorOptions = [
  '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#ef4444', '#ec4899', '#0ea5e9',
  '#84cc16', '#f97316', '#64748b', '#a855f7',
]

const newFeed = ref({ name: '', url: '', color: '#3b82f6' })

function getListColor(feed) {
  if (!feed.calendar_list_id) return '#3b82f6'
  const list = calendarLists.value.find((l) => l.id === feed.calendar_list_id)
  return list ? list.color : '#3b82f6'
}

async function fetchData() {
  loading.value = true
  try {
    const [feedsRes, listsRes] = await Promise.all([icalApi.list(), calendarListsApi.list()])
    feeds.value = feedsRes.data
    calendarLists.value = listsRes.data
  } catch (err) {
    console.error('Failed to fetch data', err)
  } finally {
    loading.value = false
  }
}

async function addFeed() {
  const { valid } = await addFormRef.value.validate()
  if (!valid) return
  adding.value = true
  try {
    const { data } = await icalApi.create(newFeed.value)
    feeds.value.unshift(data)
    addDialog.value = false
    newFeed.value = { name: '', url: '', color: '#3b82f6' }
    // Refresh lists to pick up the auto-created calendar list
    const { data: lists } = await calendarListsApi.list()
    calendarLists.value = lists
  } catch (err) {
    console.error('Failed to add feed', err)
  } finally {
    adding.value = false
  }
}

async function updateFeedColor(feed, color) {
  if (!feed.calendar_list_id) return
  try {
    await calendarListsApi.update(feed.calendar_list_id, { color })
    const idx = calendarLists.value.findIndex((l) => l.id === feed.calendar_list_id)
    if (idx !== -1) calendarLists.value[idx] = { ...calendarLists.value[idx], color }
  } catch (err) {
    console.error('Failed to update feed color', err)
  }
}

async function syncFeed(feed) {
  syncingId.value = feed.id
  try {
    const { data } = await icalApi.sync(feed.id)
    const idx = feeds.value.findIndex((f) => f.id === data.id)
    if (idx !== -1) feeds.value[idx] = data
    await fetchData()
  } catch (err) {
    console.error('Failed to sync feed', err)
  } finally {
    syncingId.value = null
  }
}

async function toggleActive(feed) {
  try {
    const { data } = await icalApi.update(feed.id, { is_active: !feed.is_active })
    const idx = feeds.value.findIndex((f) => f.id === data.id)
    if (idx !== -1) feeds.value[idx] = data
  } catch (err) {
    console.error('Failed to toggle feed', err)
  }
}

function confirmDelete(feed) {
  feedToDelete.value = feed
  deleteDialog.value = true
}

async function deleteFeed() {
  try {
    await icalApi.delete(feedToDelete.value.id)
    feeds.value = feeds.value.filter((f) => f.id !== feedToDelete.value.id)
    // Refresh lists since the linked list was deleted
    const { data: lists } = await calendarListsApi.list()
    calendarLists.value = lists
  } catch (err) {
    console.error('Failed to delete feed', err)
  }
  deleteDialog.value = false
  feedToDelete.value = null
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(fetchData)
</script>

<style scoped>
.feed-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(var(--v-theme-primary), 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.min-width-0 {
  min-width: 0;
}

.font-weight-semibold {
  font-weight: 600;
}

.color-swatch {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.15s;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.color-swatch:hover {
  transform: scale(1.2);
}

.color-swatch.selected {
  border-color: rgba(0, 0, 0, 0.4);
  transform: scale(1.15);
}

.gap-1 {
  gap: 4px;
}

.gap-2 {
  gap: 8px;
}
</style>
