import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import { configureApiRouter } from './api/index.js'
import './assets/main.css'
import '@mdi/font/css/materialdesignicons.css'

// Give the axios interceptor a reference to the router so it can use
// router.push('/login') instead of a full page reload on 401 responses.
configureApiRouter(router)

const app = createApp(App)
app.use(router)
app.mount('#app')
