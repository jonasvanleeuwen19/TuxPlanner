<template>
  <div class="md-editor">
    <!-- Tab bar -->
    <div class="md-editor-tabs">
      <button
        :class="['md-tab', activeTab === 'write' ? 'md-tab--active' : '']"
        type="button"
        @click="activeTab = 'write'"
      >
        <i class="mdi mdi-pencil-outline" /> Write
      </button>
      <button
        :class="['md-tab', activeTab === 'preview' ? 'md-tab--active' : '']"
        type="button"
        @click="activeTab = 'preview'"
      >
        <i class="mdi mdi-eye-outline" /> Preview
      </button>
      <span class="md-label">{{ label }}</span>
    </div>

    <!-- Write mode -->
    <textarea
      v-if="activeTab === 'write'"
      :value="modelValue"
      :rows="rows"
      :placeholder="placeholder"
      class="md-textarea bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <!-- Preview mode -->
    <div
      v-else
      class="md-preview bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
      v-html="renderedHtml"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Description' },
  placeholder: { type: String, default: 'Write Markdown here…' },
  rows: { type: Number, default: 3 },
})

defineEmits(['update:modelValue'])

const activeTab = ref('write')

const renderedHtml = computed(() => {
  if (!props.modelValue) return '<p class="md-empty">Nothing to preview.</p>'
  return DOMPurify.sanitize(marked.parse(props.modelValue))
})
</script>

<style scoped>
/* ── Shell ────────────────────────────────────────────────── */
.md-editor {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  overflow: hidden;
}
:global(.dark) .md-editor {
  border-color: #374151;
}

/* ── Tab bar ──────────────────────────────────────────────── */
.md-editor-tabs {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #d1d5db;
  background: #f9fafb;
  padding: 0 4px;
  gap: 2px;
}
:global(.dark) .md-editor-tabs {
  border-bottom-color: #374151;
  background: #1f2937;
}

.md-tab {
  padding: 6px 10px;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
}
:global(.dark) .md-tab {
  color: #9ca3af;
}

.md-tab--active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}
:global(.dark) .md-tab--active {
  color: #60a5fa;
  border-bottom-color: #60a5fa;
}

.md-label {
  margin-left: auto;
  font-size: 0.7rem;
  color: #9ca3af;
  padding-right: 8px;
}
:global(.dark) .md-label {
  color: #6b7280;
}

/* ── Textarea ─────────────────────────────────────────────── */
.md-textarea {
  width: 100%;
  padding: 10px 12px;
  font-size: 0.85rem;
  font-family: 'Menlo', 'Consolas', monospace;
  background: #ffffff;
  color: #111827;
  border: none;
  outline: none;
  resize: vertical;
  min-height: 80px;
  line-height: 1.6;
}
:global(.dark) .md-textarea {
  background: #111827;
  color: #f3f4f6;
}

/* ── Preview ──────────────────────────────────────────────── */
.md-preview {
  padding: 10px 12px;
  font-size: 0.85rem;
  min-height: 80px;
  color: #111827;
  background: #ffffff;
}
:global(.dark) .md-preview {
  color: #f3f4f6;
  background: #111827;
}

/* Markdown prose styles */
.md-preview :deep(p) { margin: 0 0 0.5rem; }
.md-preview :deep(p:last-child) { margin-bottom: 0; }
.md-preview :deep(h1),
.md-preview :deep(h2),
.md-preview :deep(h3),
.md-preview :deep(h4) { margin: 0.75rem 0 0.25rem; font-weight: 600; }
.md-preview :deep(h1) { font-size: 1.15rem; }
.md-preview :deep(h2) { font-size: 1.05rem; }
.md-preview :deep(h3) { font-size: 0.95rem; }
.md-preview :deep(ul),
.md-preview :deep(ol) { margin: 0.25rem 0 0.5rem 1.25rem; }
.md-preview :deep(li) { margin-bottom: 0.15rem; }
.md-preview :deep(code) {
  background: #f3f4f6;
  border-radius: 3px;
  padding: 1px 4px;
  font-family: monospace;
  font-size: 0.82em;
}
:global(.dark) .md-preview :deep(code) {
  background: #374151;
}
.md-preview :deep(pre) {
  background: #f3f4f6;
  border-radius: 6px;
  padding: 8px 12px;
  overflow-x: auto;
  margin: 0.5rem 0;
}
:global(.dark) .md-preview :deep(pre) {
  background: #374151;
}
.md-preview :deep(pre code) {
  background: transparent;
  padding: 0;
}
.md-preview :deep(blockquote) {
  border-left: 3px solid #93c5fd;
  margin: 0.5rem 0;
  padding: 0 0.75rem;
  color: #6b7280;
}
:global(.dark) .md-preview :deep(blockquote) {
  border-left-color: #3b82f6;
  color: #9ca3af;
}
.md-preview :deep(a) { color: #3b82f6; }
:global(.dark) .md-preview :deep(a) { color: #60a5fa; }
.md-preview :deep(strong) { font-weight: 600; }
.md-preview :deep(hr) {
  border-color: #e5e7eb;
  margin: 0.75rem 0;
}
:global(.dark) .md-preview :deep(hr) {
  border-color: #374151;
}
.md-empty { color: #9ca3af; font-style: italic; }
:global(.dark) .md-empty { color: #6b7280; }
</style>

