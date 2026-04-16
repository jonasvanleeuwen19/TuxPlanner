import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Events ────────────────────────────────────────────────────────────────────

export const eventsApi = {
  list: (params = {}) => api.get('/events/', { params }),
  get: (id) => api.get(`/events/${id}`),
  create: (data) => api.post('/events/', data),
  update: (id, data) => api.put(`/events/${id}`, data),
  delete: (id) => api.delete(`/events/${id}`),
}

// ── Todos ─────────────────────────────────────────────────────────────────────

export const todosApi = {
  list: () => api.get('/todos/'),
  get: (id) => api.get(`/todos/${id}`),
  create: (data) => api.post('/todos/', data),
  update: (id, data) => api.put(`/todos/${id}`, data),
  delete: (id) => api.delete(`/todos/${id}`),
}

export default api
