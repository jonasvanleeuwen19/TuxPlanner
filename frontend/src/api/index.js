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
  list: () => api.get('/todos/'),
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

export default api
