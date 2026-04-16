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
    theme: {
      defaultTheme: 'light',
      themes: {
        light: {
          colors: {
            primary: '#1565C0',
            secondary: '#42A5F5',
            accent: '#0288D1',
            surface: '#FFFFFF',
            background: '#F5F7FA',
          },
        },
        dark: {
          colors: {
            primary: '#42A5F5',
            secondary: '#1565C0',
            accent: '#0288D1',
          },
        },
      },
    },
  })
}
