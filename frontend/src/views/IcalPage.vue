<template>
  <div class="p-4 md:p-6">
    <div class="flex items-center mb-6">
      <div>
        <h1 class="text-xl font-bold">External Calendars</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">Automatically syncs every hour</p>
      </div>
      <div class="flex-1" />
      <button
        class="flex items-center gap-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
        @click="addDialog = true"
      >
        <i class="mdi mdi-plus" />
        Add Calendar
      </button>
    </div>

    <div v-if="loading" class="w-full h-1 bg-gray-200 dark:bg-gray-800 rounded mb-4 overflow-hidden">
      <div class="h-full bg-blue-500 animate-pulse w-full" />
    </div>

    <div v-if="feeds.length === 0 && !loading" class="text-center py-16">
      <i class="mdi mdi-calendar-sync-outline text-6xl text-blue-300 dark:text-gray-600 block mb-4" />
      <h3 class="text-base font-medium text-gray-500 dark:text-gray-400">No external calendars added</h3>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Add an ICAL URL or CalDAV calendar to sync</p>
      <button
        class="mt-4 inline-flex items-center gap-1 px-4 py-2 bg-blue-50 dark:bg-gray-700 hover:bg-blue-100 text-blue-600 dark:text-blue-400 rounded-lg text-sm font-medium transition-colors"
        @click="addDialog = true"
      >
        <i class="mdi mdi-plus" />
        Add your first calendar
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
            <i
              :class="['mdi text-lg', feed.feed_type === 'caldav' ? 'mdi-server' : 'mdi-calendar-sync-outline']"
              :style="{ color: getListColor(feed) }"
            />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ feed.name }}</p>
              <span class="text-xs px-1.5 py-0.5 rounded font-medium bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 uppercase">
                {{ feed.feed_type || 'ical' }}
              </span>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{{ feed.url }}</p>
          </div>
          <span
            :class="[
              'ml-2 shrink-0 text-xs px-2 py-0.5 rounded-md font-medium',
              feed.is_active
                ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
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

        <!-- Calendar list visibility toggles -->
        <div v-if="getListsForFeed(feed).length > 0" class="mb-3 space-y-1">
          <p class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
            <i class="mdi mdi-calendar-multiple-check mr-1" />Calendars
          </p>
          <div
            v-for="list in getListsForFeed(feed)"
            :key="list.id"
            class="flex items-center gap-2 py-1"
          >
            <div class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: list.color }" />
            <span class="text-xs flex-1 truncate text-gray-700 dark:text-gray-300">
              {{ list.caldav_calendar_name || list.name }}
            </span>
            <button
              :class="[
                'relative inline-flex h-4 w-7 items-center rounded-full transition-colors shrink-0',
                list.is_visible ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
              ]"
              @click="toggleListVisibility(list)"
            >
              <span
                :class="[
                  'inline-block h-3 w-3 transform rounded-full bg-white transition-transform',
                  list.is_visible ? 'translate-x-3.5' : 'translate-x-0.5'
                ]"
              />
            </button>
          </div>
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

    <!-- Add Calendar Dialog -->
    <Teleport to="body">
      <div
        v-if="addDialog"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="addDialog = false"
      >
        <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          <div class="flex items-center p-5 pb-3 sticky top-0 bg-white dark:bg-gray-900">
            <div class="w-9 h-9 rounded-xl bg-blue-100 dark:bg-gray-700 flex items-center justify-center mr-3">
              <i class="mdi mdi-calendar-plus text-blue-500 dark:text-blue-400" />
            </div>
            <span class="text-base font-bold text-gray-900 dark:text-gray-100">Add External Calendar</span>
            <div class="flex-1" />
            <button class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400" @click="addDialog = false">
              <i class="mdi mdi-close" />
            </button>
          </div>
          <hr class="border-gray-200 dark:border-gray-800" />
          <div class="p-5 space-y-3">
            <!-- Feed type selector -->
            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Calendar type</label>
              <div class="flex rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <button
                  :class="[
                    'flex-1 px-3 py-2 text-xs font-medium transition-colors flex items-center justify-center gap-1',
                    newFeed.feed_type === 'ical'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                  ]"
                  @click="newFeed.feed_type = 'ical'"
                >
                  <i class="mdi mdi-calendar-sync-outline" /> ICAL / WebCal
                </button>
                <button
                  :class="[
                    'flex-1 px-3 py-2 text-xs font-medium transition-colors flex items-center justify-center gap-1',
                    newFeed.feed_type === 'caldav'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                  ]"
                  @click="newFeed.feed_type = 'caldav'"
                >
                  <i class="mdi mdi-server" /> CalDAV
                </button>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Calendar name</label>
              <div class="relative">
                <i class="mdi mdi-label-outline absolute left-3 top-2.5 text-gray-400" />
                <input
                  v-model="newFeed.name"
                  type="text"
                  placeholder="My Calendar"
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <p v-if="addErrors.name" class="text-xs text-red-500 mt-1">{{ addErrors.name }}</p>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ newFeed.feed_type === 'caldav' ? 'CalDAV server URL' : 'ICAL URL (.ics)' }}
              </label>
              <div class="relative">
                <i class="mdi mdi-link absolute left-3 top-2.5 text-gray-400" />
                <input
                  v-model="newFeed.url"
                  type="text"
                  :placeholder="newFeed.feed_type === 'caldav' ? 'https://caldav.example.com/...' : 'https://...'"
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <p v-if="addErrors.url" class="text-xs text-red-500 mt-1">{{ addErrors.url }}</p>
              <p class="text-xs text-gray-500 mt-1">
                {{ newFeed.feed_type === 'caldav' ? 'Enter the CalDAV principal or calendar URL' : "Paste your calendar's .ics subscribe link" }}
              </p>
            </div>

            <!-- CalDAV credentials -->
            <template v-if="newFeed.feed_type === 'caldav'">
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
                <div class="relative">
                  <i class="mdi mdi-account-outline absolute left-3 top-2.5 text-gray-400" />
                  <input
                    v-model="newFeed.caldav_username"
                    type="text"
                    placeholder="Username"
                    class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
                <div class="relative">
                  <i class="mdi mdi-lock-outline absolute left-3 top-2.5 text-gray-400" />
                  <input
                    v-model="newFeed.caldav_password"
                    type="password"
                    placeholder="Password"
                    class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </template>

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
            <h2 class="text-base font-bold text-gray-900 dark:text-gray-100">Remove Calendar</h2>
          </div>
          <div class="px-5 pb-4 text-sm text-gray-600 dark:text-gray-400">
            Remove <strong class="text-gray-900 dark:text-gray-100">{{ feedToDelete?.name }}</strong>? All imported events from this calendar will be deleted.
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

const newFeed = ref({ name: '', url: '', color: '#3b82f6', feed_type: 'ical', caldav_username: '', caldav_password: '' })

function getListColor(feed) {
  if (!feed.calendar_list_id) return '#3b82f6'
  const list = calendarLists.value.find((l) => l.id === feed.calendar_list_id)
  return list ? list.color : '#3b82f6'
}

function getListsForFeed(feed) {
  return calendarLists.value.filter((l) => l.ical_feed_id === feed.id)
}

async function toggleListVisibility(list) {
  try {
    await calendarListsApi.update(list.id, { is_visible: !list.is_visible })
    const idx = calendarLists.value.findIndex((l) => l.id === list.id)
    if (idx !== -1) calendarLists.value[idx] = { ...calendarLists.value[idx], is_visible: !list.is_visible }
  } catch (err) {
    console.error('Failed to toggle visibility', err)
  }
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
    const { data } = await icalApi.create({
      name: newFeed.value.name,
      url: newFeed.value.url,
      color: newFeed.value.color,
      feed_type: newFeed.value.feed_type,
      caldav_username: newFeed.value.caldav_username || null,
      caldav_password: newFeed.value.caldav_password || null,
    })
    feeds.value.unshift(data)
    addDialog.value = false
    newFeed.value = { name: '', url: '', color: '#3b82f6', feed_type: 'ical', caldav_username: '', caldav_password: '' }
    const { data: lists } = await calendarListsApi.list()
    calendarLists.value = lists
  } catch (err) {
    console.error('Failed to add calendar', err)
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
    console.error('Failed to update calendar color', err)
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
    console.error('Failed to sync calendar', err)
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
    console.error('Failed to toggle calendar', err)
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
    console.error('Failed to delete calendar', err)
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
