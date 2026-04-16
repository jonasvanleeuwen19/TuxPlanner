import { createRouter, createWebHistory } from 'vue-router'
import CalendarPage from '../views/CalendarPage.vue'
import TodoPage from '../views/TodoPage.vue'
import IcalPage from '../views/IcalPage.vue'

const routes = [
  { path: '/', component: CalendarPage },
  { path: '/todos', component: TodoPage },
  { path: '/ical', component: IcalPage },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
