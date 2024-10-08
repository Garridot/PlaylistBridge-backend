import re

def password_validator(password):
    """Verifica que la contraseña sea segura."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Al menos una mayúscula
        return False
    if not re.search(r'[a-z]', password):  # Al menos una minúscula
        return False
    if not re.search(r'[0-9]', password):  # Al menos un número
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Al menos un símbolo especial
        return False
    return True
