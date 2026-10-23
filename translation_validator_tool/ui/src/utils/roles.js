export const ROLE_ADMIN = 'admin';
export const ROLE_BOTH = 'ambos';
export const ACTIVE_TRANSLATOR = 'translation';
export const ACTIVE_VALIDATOR = 'validation';

const ACTIVE_ROLE_KEY = 'active_role';

export const getUserRole = (user) => {
  if (!user) return null;
  if (user.is_superuser) return ROLE_ADMIN;
  return user.role || ROLE_BOTH;
};

export const isAdmin = (user) => getUserRole(user) === ROLE_ADMIN;

export const canTranslate = (user) => isAdmin(user) || getUserRole(user) === ROLE_BOTH;

export const canValidate = (user) => isAdmin(user) || getUserRole(user) === ROLE_BOTH;

export const isValidActiveRole = (role) => role === ACTIVE_TRANSLATOR || role === ACTIVE_VALIDATOR;

export const getStoredActiveRole = (user) => {
  if (!user || isAdmin(user)) return null;

  const storedRole = localStorage.getItem(ACTIVE_ROLE_KEY);
  if (storedRole === ACTIVE_VALIDATOR && canValidate(user)) return ACTIVE_VALIDATOR;
  if (storedRole === ACTIVE_TRANSLATOR && canTranslate(user)) return ACTIVE_TRANSLATOR;

  if (canTranslate(user)) return ACTIVE_TRANSLATOR;
  if (canValidate(user)) return ACTIVE_VALIDATOR;
  return null;
};

export const setStoredActiveRole = (role) => {
  if (!isValidActiveRole(role)) return;
  localStorage.setItem(ACTIVE_ROLE_KEY, role);
};

export const removeStoredActiveRole = () => {
  localStorage.removeItem(ACTIVE_ROLE_KEY);
};

export const routeForActiveRole = (role) => {
  if (role === ACTIVE_VALIDATOR) return '/validator';
  return '/translator-annotations';
};
