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
            primary: '#3b82f6',
            secondary: '#60a5fa',
            accent: '#06b6d4',
            surface: '#ffffff',
            background: '#f8fafc',
            error: '#ef4444',
            warning: '#f59e0b',
            success: '#10b981',
            info: '#3b82f6',
          },
        },
        dark: {
          colors: {
            primary: '#60a5fa',
            secondary: '#93c5fd',
            accent: '#38bdf8',
            surface: '#1c1c1c',
            background: '#111111',
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
