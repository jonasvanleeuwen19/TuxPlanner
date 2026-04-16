import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const eventsApi = {
  list: (params = {}) => api.get('/events/', { params }),
  get: (id) => api.get(`/events/${id}`),
  create: (data) => api.post('/events/', data),
  update: (id, data) => api.put(`/events/${id}`, data),
  delete: (id) => api.delete(`/events/${id}`),
}

export const todosApi = {
  list: (params = {}) => api.get('/todos/', { params }),
  get: (id) => api.get(`/todos/${id}`),
  create: (data) => api.post('/todos/', data),
  update: (id, data) => api.put(`/todos/${id}`, data),
  delete: (id) => api.delete(`/todos/${id}`),
}

export const icalApi = {
  list: () => api.get('/ical-feeds/'),
  get: (id) => api.get(`/ical-feeds/${id}`),
  create: (data) => api.post('/ical-feeds/', data),
  update: (id, data) => api.put(`/ical-feeds/${id}`, data),
  delete: (id) => api.delete(`/ical-feeds/${id}`),
  sync: (id) => api.post(`/ical-feeds/${id}/sync`),
}

export const calendarListsApi = {
  list: () => api.get('/calendar-lists/'),
  get: (id) => api.get(`/calendar-lists/${id}`),
  create: (data) => api.post('/calendar-lists/', data),
  update: (id, data) => api.put(`/calendar-lists/${id}`, data),
  delete: (id) => api.delete(`/calendar-lists/${id}`),
}

export const todoListsApi = {
  list: () => api.get('/todo-lists/'),
  get: (id) => api.get(`/todo-lists/${id}`),
  create: (data) => api.post('/todo-lists/', data),
  update: (id, data) => api.put(`/todo-lists/${id}`, data),
  delete: (id) => api.delete(`/todo-lists/${id}`),
}

export const subtaskCategoriesApi = {
  list: () => api.get('/subtask-categories/'),
  create: (data) => api.post('/subtask-categories/', data),
  update: (id, data) => api.put(`/subtask-categories/${id}`, data),
  delete: (id) => api.delete(`/subtask-categories/${id}`),
}

export const subtasksApi = {
  list: (eventId) => api.get(`/events/${eventId}/subtasks/`),
  create: (eventId, data) => api.post(`/events/${eventId}/subtasks/`, data),
  update: (eventId, subtaskId, data) => api.put(`/events/${eventId}/subtasks/${subtaskId}`, data),
  delete: (eventId, subtaskId) => api.delete(`/events/${eventId}/subtasks/${subtaskId}`),
}

export default api
