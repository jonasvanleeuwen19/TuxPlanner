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
      class="md-textarea"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <!-- Preview mode -->
    <div
      v-else
      class="md-preview prose dark:prose-invert"
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
.md-editor {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  overflow: hidden;
}

.md-editor-tabs {
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-on-surface), 0.03);
  padding: 0 4px;
  gap: 2px;
}

.md-tab {
  padding: 6px 10px;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: rgba(var(--v-theme-on-surface), 0.6);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.md-tab--active {
  color: rgb(var(--v-theme-primary));
  border-bottom-color: rgb(var(--v-theme-primary));
}

.md-label {
  margin-left: auto;
  font-size: 0.7rem;
  color: rgba(var(--v-theme-on-surface), 0.4);
  padding-right: 8px;
}

.md-textarea {
  width: 100%;
  padding: 10px 12px;
  font-size: 0.85rem;
  font-family: 'Menlo', 'Consolas', monospace;
  background: transparent;
  color: rgba(var(--v-theme-on-surface), 0.87);
  border: none;
  outline: none;
  resize: vertical;
  min-height: 80px;
  line-height: 1.6;
}

.md-preview {
  padding: 10px 12px;
  font-size: 0.85rem;
  min-height: 80px;
  color: rgba(var(--v-theme-on-surface), 0.87);
}

/* Minimal Markdown prose styles */
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
  background: rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 3px;
  padding: 1px 4px;
  font-family: monospace;
  font-size: 0.82em;
}
.md-preview :deep(pre) {
  background: rgba(var(--v-theme-on-surface), 0.06);
  border-radius: 6px;
  padding: 8px 12px;
  overflow-x: auto;
  margin: 0.5rem 0;
}
.md-preview :deep(pre code) {
  background: transparent;
  padding: 0;
}
.md-preview :deep(blockquote) {
  border-left: 3px solid rgba(var(--v-theme-primary), 0.5);
  margin: 0.5rem 0;
  padding: 0 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}
.md-preview :deep(a) { color: rgb(var(--v-theme-primary)); }
.md-preview :deep(strong) { font-weight: 600; }
.md-preview :deep(hr) { border-color: rgba(var(--v-border-color), var(--v-border-opacity)); margin: 0.75rem 0; }
.md-empty { color: rgba(var(--v-theme-on-surface), 0.4); font-style: italic; }
</style>
