import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Devices API
export const devicesAPI = {
  getAll: () => api.get('/devices/'),
  getOne: (id) => api.get(`/devices/${id}/`),
  toggle: (id) => api.post(`/devices/${id}/toggle/`),
  getSummary: () => api.get('/devices/summary/'),
  create: (data) => api.post('/devices/', data),
  update: (id, data) => api.put(`/devices/${id}/`, data),
  delete: (id) => api.delete(`/devices/${id}/`),
  getHistory: (id) => api.get(`/devices/${id}/history/`),
  getErrors: (id) => api.get(`/devices/${id}/errors/`),
};

// Energy API
export const energyAPI = {
  getCurrent: () => api.get('/energy/current/'),
  getToday: () => api.get('/energy/today/'),
  getHourly: (date) => api.get(`/energy/hourly/?date=${date}`),
  getDaily: (year, month) => api.get(`/energy/daily/?year=${year}&month=${month}`),
  getMonthly: (year) => api.get(`/energy/monthly/?year=${year}`),
  getStatistics: () => api.get('/energy/statistics/'),
  getTopConsumers: () => api.get('/energy/top_consumers/'),
  getForecast: () => api.get('/energy/forecast/'),
  getComparison: (period) => api.get(`/energy/comparison/?period=${period}`),
  getExportData: (format) => api.get(`/energy/export/?format=${format}`),
};


export default api;
