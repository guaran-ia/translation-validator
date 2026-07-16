def is_admin(user) -> bool:
    return bool(getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin')


def can_translate(user) -> bool:
    return is_admin(user) or getattr(user, 'role', None) == 'ambos'


def can_validate(user) -> bool:
    return is_admin(user) or getattr(user, 'role', None) == 'ambos'
