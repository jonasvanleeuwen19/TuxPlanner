<template>
  <div class="p-4 md:p-6">
    <div class="flex items-center mb-6">
      <div>
        <h1 class="text-xl font-bold">ICAL Sync</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">Automatically syncs every hour</p>
      </div>
      <div class="flex-1" />
      <button
        class="flex items-center gap-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
        @click="addDialog = true"
      >
        <i class="mdi mdi-plus" />
        Add Feed
      </button>
    </div>

    <div v-if="loading" class="w-full h-1 bg-gray-200 dark:bg-gray-800 rounded mb-4 overflow-hidden">
      <div class="h-full bg-blue-500 animate-pulse w-full" />
    </div>

    <div v-if="feeds.length === 0 && !loading" class="text-center py-16">
      <i class="mdi mdi-calendar-sync-outline text-6xl text-blue-300 dark:text-gray-600 block mb-4" />
      <h3 class="text-base font-medium text-gray-500 dark:text-gray-400">No ICAL feeds added</h3>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Add an ICAL URL to sync external calendars</p>
      <button
        class="mt-4 inline-flex items-center gap-1 px-4 py-2 bg-blue-50 dark:bg-gray-700 hover:bg-blue-100 text-blue-600 dark:text-blue-400 rounded-lg text-sm font-medium transition-colors"
        @click="addDialog = true"
      >
        <i class="mdi mdi-plus" />
        Add your first feed
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="feed in feeds"
        :key="feed.id"
        class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-4"
      >
        <div class="flex items-start mb-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 mr-3"
            :style="{ background: `${getListColor(feed)}22` }"
          >
            <i class="mdi mdi-calendar-sync-outline text-lg" :style="{ color: getListColor(feed) }" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold">{{ feed.name }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{{ feed.url }}</p>
          </div>
          <span
            :class="[
              'ml-2 shrink-0 text-xs px-2 py-0.5 rounded-md font-medium',
              feed.is_active
                ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-500'
            ]"
          >
            {{ feed.is_active ? 'Active' : 'Paused' }}
          </span>
        </div>

        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          <i class="mdi mdi-clock-sync-outline mr-1" />
          {{ feed.last_synced ? `Last synced ${formatDateTime(feed.last_synced)}` : 'Never synced' }}
        </p>

        <div class="flex items-center mb-3 flex-wrap gap-1">
          <span class="text-xs text-gray-500 dark:text-gray-400 mr-1">Color:</span>
          <div
            v-for="color in colorOptions"
            :key="color"
            class="w-5 h-5 rounded-full cursor-pointer transition-transform border-2 hover:scale-110 shrink-0"
            :style="{ backgroundColor: color, borderColor: getListColor(feed) === color ? 'rgba(0,0,0,0.4)' : 'transparent' }"
            @click="updateFeedColor(feed, color)"
          />
        </div>

        <div class="flex gap-2 items-center">
          <button
            :disabled="syncingId === feed.id"
            class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-50 dark:bg-gray-700 text-blue-600 dark:text-blue-400 hover:bg-blue-100 transition-colors disabled:opacity-50"
            @click="syncFeed(feed)"
          >
            <i :class="['mdi mdi-refresh', syncingId === feed.id ? 'animate-spin' : '']" />
            Sync now
          </button>
          <button
            :class="[
              'flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors',
              feed.is_active
                ? 'bg-amber-50 dark:bg-gray-700 text-amber-600 dark:text-amber-400 hover:bg-amber-100'
                : 'bg-green-50 dark:bg-gray-700 text-green-600 dark:text-green-400 hover:bg-green-100'
            ]"
            @click="toggleActive(feed)"
          >
            <i :class="['mdi', feed.is_active ? 'mdi-pause' : 'mdi-play']" />
            {{ feed.is_active ? 'Pause' : 'Resume' }}
          </button>
          <div class="flex-1" />
          <button
            class="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-400 hover:text-red-500 transition-colors"
            @click="confirmDelete(feed)"
          >
            <i class="mdi mdi-trash-can-outline" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add Feed Dialog -->
    <Teleport to="body">
      <div
        v-if="addDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="addDialog = false"
      >
        <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md">
          <div class="flex items-center p-5 pb-3">
            <div class="w-9 h-9 rounded-xl bg-blue-100 dark:bg-gray-700 flex items-center justify-center mr-3">
              <i class="mdi mdi-calendar-plus text-blue-500 dark:text-blue-400" />
            </div>
            <span class="text-base font-bold">Add ICAL Feed</span>
            <div class="flex-1" />
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800" @click="addDialog = false">
              <i class="mdi mdi-close" />
            </button>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="p-5 space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Feed name</label>
              <div class="relative">
                <i class="mdi mdi-label-outline absolute left-3 top-2.5 text-gray-400" />
                <input
                  v-model="newFeed.name"
                  type="text"
                  placeholder="My Calendar"
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <p v-if="addErrors.name" class="text-xs text-red-500 mt-1">{{ addErrors.name }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">ICAL URL (.ics)</label>
              <div class="relative">
                <i class="mdi mdi-link absolute left-3 top-2.5 text-gray-400" />
                <input
                  v-model="newFeed.url"
                  type="text"
                  placeholder="https://..."
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <p v-if="addErrors.url" class="text-xs text-red-500 mt-1">{{ addErrors.url }}</p>
              <p class="text-xs text-gray-500 mt-1">Paste your calendar's .ics subscribe link</p>
            </div>
            <div>
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Calendar color</p>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="color in colorOptions"
                  :key="color"
                  class="w-6 h-6 rounded-full cursor-pointer transition-transform border-2 hover:scale-110 shrink-0"
                  :style="{ backgroundColor: color, borderColor: newFeed.color === color ? 'rgba(0,0,0,0.4)' : 'transparent' }"
                  @click="newFeed.color = color"
                />
              </div>
            </div>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="flex justify-end gap-2 p-4">
            <button
              class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              @click="addDialog = false"
            >
              Cancel
            </button>
            <button
              :disabled="adding"
              class="flex items-center gap-1 px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              @click="addFeed"
            >
              <i v-if="adding" class="mdi mdi-loading animate-spin" />
              Add &amp; Sync
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirm Dialog -->
    <Teleport to="body">
      <div
        v-if="deleteDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="deleteDialog = false"
      >
        <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-sm">
          <div class="p-5 pb-3">
            <h2 class="text-base font-bold">Remove Feed</h2>
          </div>
          <div class="px-5 pb-4 text-sm text-gray-600 dark:text-gray-400">
            Remove <strong class="text-gray-900 dark:text-gray-100">{{ feedToDelete?.name }}</strong>? All imported events from this feed will be deleted.
          </div>
          <div class="flex justify-end gap-2 p-4">
            <button
              class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              @click="deleteDialog = false"
            >
              Cancel
            </button>
            <button
              class="px-4 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
              @click="deleteFeed"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
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
const adding = ref(false)
const syncingId = ref(null)
const addErrors = ref({ name: '', url: '' })

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
  addErrors.value = { name: '', url: '' }
  let valid = true
  if (!newFeed.value.name) { addErrors.value.name = 'Name is required'; valid = false }
  if (!newFeed.value.url) { addErrors.value.url = 'URL is required'; valid = false }
  else if (!/^(https?|webcals?):\/\//.test(newFeed.value.url)) { addErrors.value.url = 'Must be a valid URL'; valid = false }
  if (!valid) return
  adding.value = true
  try {
    const { data } = await icalApi.create(newFeed.value)
    feeds.value.unshift(data)
    addDialog.value = false
    newFeed.value = { name: '', url: '', color: '#3b82f6' }
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
  return new Date(dateStr).toLocaleDateString('en-US', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

onMounted(fetchData)
</script>
