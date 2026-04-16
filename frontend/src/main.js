import { createApp } from 'vue'
import App from './App.vue'
import { createVuetify } from './plugins/vuetify'

import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'

const app = createApp(App)
app.use(createVuetify())
app.mount('#app')
