import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const scheduleAPI = {
  // Расписания
  getAll: (deviceId, status) => {
    let url = `${API_URL}/schedules/`;
    const params = new URLSearchParams();
    if (deviceId) params.append('device_id', deviceId);
    if (status) params.append('status', status);
    if (params.toString()) url += `?${params.toString()}`;
    return axios.get(url);
  },
  
  getOne: (id) => axios.get(`${API_URL}/schedules/${id}/`),
  create: (data) => axios.post(`${API_URL}/schedules/`, data),
  update: (id, data) => axios.put(`${API_URL}/schedules/${id}/`, data),
  delete: (id) => axios.delete(`${API_URL}/schedules/${id}/`),
  
  // Действия
  activate: (id) => axios.post(`${API_URL}/schedules/${id}/activate/`),
  deactivate: (id) => axios.post(`${API_URL}/schedules/${id}/deactivate/`),
  history: (id, days = 30) => axios.get(`${API_URL}/schedules/${id}/history/?days=${days}`),
  
  // Шаблоны
  getTemplates: (deviceType) => {
    let url = `${API_URL}/schedules/templates/`;
    if (deviceType) url += `?device_type=${deviceType}`;
    return axios.get(url);
  },
  
  createFromTemplate: (templateId, deviceId) =>
    axios.post(`${API_URL}/schedules/from_template/`, {
      template_id: templateId,
      device_id: deviceId,
    }),
};
