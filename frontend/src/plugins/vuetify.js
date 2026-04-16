import { createVuetify as _createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

export function createVuetify() {
  return _createVuetify({
    components,
    directives,
    icons: {
      defaultSet: 'mdi',
      aliases,
      sets: { mdi },
    },
    defaults: {
      VCard: { rounded: 'xl' },
      VBtn: { rounded: 'lg' },
      VTextField: { rounded: 'lg' },
      VTextarea: { rounded: 'lg' },
      VSelect: { rounded: 'lg' },
      VDialog: { rounded: 'xl' },
      VChip: { rounded: 'lg' },
    },
    theme: {
      defaultTheme: 'light',
      themes: {
        light: {
          colors: {
            primary: '#6366f1',
            secondary: '#8b5cf6',
            accent: '#06b6d4',
            surface: '#ffffff',
            background: '#f1f5f9',
            error: '#ef4444',
            warning: '#f59e0b',
            success: '#10b981',
            info: '#3b82f6',
          },
        },
        dark: {
          colors: {
            primary: '#818cf8',
            secondary: '#a78bfa',
            accent: '#22d3ee',
            surface: '#1e1e2e',
            background: '#0f0f1a',
            error: '#f87171',
            warning: '#fbbf24',
            success: '#34d399',
            info: '#60a5fa',
          },
        },
      },
    },
  })
}
