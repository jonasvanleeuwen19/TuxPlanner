import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './assets/main.css'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const savedTheme = localStorage.getItem('theme') || 'light'

const vuetify = createVuetify({
  components,
  directives,
  icons: { defaultSet: 'mdi' },
  theme: {
    defaultTheme: savedTheme === 'dark' ? 'customDark' : 'customLight',
    themes: {
      customLight: {
        dark: false,
        colors: {
          primary: '#3b82f6',
          secondary: '#8b5cf6',
          background: '#f9fafb',
          surface: '#ffffff',
          error: '#ef4444',
        },
      },
      customDark: {
        dark: true,
        colors: {
          primary: '#60a5fa',
          secondary: '#a78bfa',
          background: '#030712',
          surface: '#111827',
          'surface-variant': '#1f2937',
          error: '#f87171',
        },
      },
    },
  },
})

const app = createApp(App)
app.use(router)
app.use(vuetify)
app.mount('#app')
