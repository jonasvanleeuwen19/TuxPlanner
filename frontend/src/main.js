import { createApp } from 'vue'
import App from './App.vue'
import { createVuetify } from './plugins/vuetify'
import router from './router/index.js'

import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'

const app = createApp(App)
app.use(createVuetify())
app.use(router)
app.mount('#app')
