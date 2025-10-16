import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register: (userData) => 
    api.post('/auth/register', userData),
  getCurrentUser: () => 
    api.get('/auth/me'),
};

// Translations API
export const translationsAPI = {
  getById: (id) => 
    api.get(`/translations/${id}`),
  getNext: () => 
    api.get('/translations/next'),
  getNextFrom: (currentId) => 
    api.get(`/translations/navigation/next/${currentId}`),
  getPrevious: (currentId) => 
    api.get(`/translations/navigation/previous/${currentId}`),
  getRandom: () => 
    axios.get(`${API_URL}/translations/random`), // Sin autenticación
  getStats: () => 
    api.get('/translations/stats'),
  getPublicStats: () => 
    axios.get(`${API_URL}/translations/stats/public`), // Sin autenticación
  getMyValidatedHistory: (skip = 0, limit = 20) => 
    api.get(`/translations/validated/my-history?skip=${skip}&limit=${limit}`),
  getMyPendingTranslations: (skip = 0, limit = 20) => 
    api.get(`/translations/pending/for-me?skip=${skip}&limit=${limit}`),
};

// Validations API
export const validationsAPI = {
  create: (data) => 
    api.post('/validations', data),
  update: (id, data) => 
    api.put(`/validations/${id}`, data),
  getMyHistory: (skip = 0, limit = 50) => 
    api.get(`/validations/my-history?skip=${skip}&limit=${limit}`),
  getByTranslation: (translationId) => 
    api.get(`/validations/by-translation/${translationId}`),
};

// Suggestions API
export const suggestionsAPI = {
  create: (data) => 
    api.post('/suggestions', data),
  getByTranslation: (translationId) => 
    api.get(`/suggestions?translation_id=${translationId}`),
  getMySuggestions: (skip = 0, limit = 50) => 
    api.get(`/suggestions/my-suggestions?skip=${skip}&limit=${limit}`),
  getStats: () => 
    api.get('/suggestions/stats'),
  delete: (suggestionId) => 
    api.delete(`/suggestions/${suggestionId}`),
};

export default api;