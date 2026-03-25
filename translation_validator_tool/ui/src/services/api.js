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
    
    // No forzar Content-Type para FormData - dejar que el navegador lo configure
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
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
    // Use plain axios to avoid the global 401 interceptor which would force a full-page
    // redirect to /login on unauthorized responses. We want the login form to handle
    // invalid credentials inline without reloading.
    return axios.post(`${API_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register: (userData) => 
    api.post('/auth/register', userData),
  getCurrentUser: () => 
    api.get('/auth/me'),
  // Admin endpoints
  getAllUsers: () =>
    api.get('/auth/users'),
  getPendingRegistrations: () =>
    api.get('/auth/pending'),
  approveUser: (userId) =>
    api.patch(`/auth/approve/${userId}`),
  updateUser: (userId, updates) =>
    api.patch(`/auth/admin/users/${userId}`, updates),
  deleteUser: (userId) =>
    api.delete(`/auth/admin/users/${userId}`),
  changeUserPassword: (userId, newPassword) =>
    api.post(`/auth/admin/change-password/${userId}`, { new_password: newPassword }),
  changeOwnPassword: (currentPassword, newPassword) =>
    api.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword }),
};

// Translations API
export const translationsAPI = {
  getById: (id) => 
    api.get(`/translations/${id}`),
  getPair: (id) =>
    api.get(`/translations/pair/${id}`),
  getContext: (id, before = 2, after = 2) =>
    api.get(`/translations/context/${id}?before=${before}&after=${after}`),
  getNext: () => 
    api.get('/translations/next'),
  getNextSuitable: () =>
    api.get('/translations/next/suitable'),
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
  getAdminList: (skip = 0, limit = 20, q = '') =>
    api.get(`/translations/admin/list?skip=${skip}&limit=${limit}${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  updateDirection: (translationId, direction) =>
    api.patch(`/translations/${translationId}/direction`, { direction }),
  adminCreate: (data) =>
    api.post('/translations/admin/create', data),
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

// Annotations API
export const annotationsAPI = {
  getAll: (skip = 0, limit = 20, q = '') =>
    api.get(`/annotations?skip=${skip}&limit=${limit}${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  getById: (id) => 
    api.get(`/annotations/${id}`),
  getAvailableForTranslation: (skip = 0, limit = 20) =>
    api.get(`/annotations/available-for-translation?skip=${skip}&limit=${limit}`),
  create: (data) =>
    api.post('/annotations', data),
  update: (id, data) =>
    api.put(`/annotations/${id}`, data),
  delete: (id) =>
    api.delete(`/annotations/${id}`),
  assign: (id, data) =>
    api.put(`/annotations/${id}/assign`, data),
  validate: (id, data) =>
    api.post(`/annotations/${id}/validate`, data),
  suggest: (id, data) =>
    api.post(`/annotations/${id}/suggest`, data),
  getStats: () =>
    api.get('/annotations/stats'),
  
  // Multi-user assignment endpoints
  getAssignments: (annotationId) =>
    api.get(`/annotations/${annotationId}/assignments`),
  assignUser: (annotationId, userId) =>
    api.post(`/annotations/${annotationId}/assign?user_id=${userId}`),
  unassignUser: (annotationId, userId) =>
    api.delete(`/annotations/${annotationId}/assign/${userId}`),
  bulkAssign: (data) =>
    api.post('/annotations/assign/bulk', data),
  
  // Multi-user translation endpoints
  getTranslations: (annotationId) =>
    api.get(`/annotations/${annotationId}/translations`),
  getTranslationByUser: (annotationId, userId) =>
    api.get(`/annotations/${annotationId}/translations/${userId}`),
  createTranslation: (annotationId, data) =>
    api.post(`/annotations/${annotationId}/translations`, data),
  updateTranslation: (annotationId, translationId, data) =>
    api.put(`/annotations/${annotationId}/translations/${translationId}`, data),
  deleteTranslation: (annotationId, translationId) =>
    api.delete(`/annotations/${annotationId}/translations/${translationId}`),
  bulkCreateTranslations: (data) =>
    api.post('/annotations/translations/bulk', data),
  getMyAssignments: () =>
    api.get('/annotations/my-assignments'),
  getMyTranslations: () =>
    api.get('/annotations/my-translations'),
};

export default api;