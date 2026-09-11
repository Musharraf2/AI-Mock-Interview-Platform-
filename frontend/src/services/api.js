import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT token if stored
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const authApi = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
};

export const interviewApi = {
  startSession: (sessionParams) => api.post('/interview/start', sessionParams),
  submitAnswer: (answerParams) => api.post('/interview/submit-answer', answerParams),
  getMySessions: () => api.get('/interview/my-sessions'),
  getSessionDetails: (sessionId) => api.get(`/interview/session/${sessionId}`),
};

export const analyticsApi = {
  getDashboardMetrics: () => api.get('/analytics/dashboard'),
};

export default api;
