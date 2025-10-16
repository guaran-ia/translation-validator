// Authentication utilities
export const getStoredToken = () => {
  return localStorage.getItem('access_token');
};

export const setStoredToken = (token) => {
  localStorage.setItem('access_token', token);
};

export const removeStoredToken = () => {
  localStorage.removeItem('access_token');
};

export const isAuthenticated = () => {
  const token = getStoredToken();
  if (!token) return false;
  
  try {
    // Simple check for token expiration
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp > currentTime;
  } catch (error) {
    return false;
  }
};