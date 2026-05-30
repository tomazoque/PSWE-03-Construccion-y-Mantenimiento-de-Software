from __future__ import annotations

import re


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PASSWORD_PATTERN = re.compile(r"^[A-Za-z0-9#]+$")
TOKEN_PATTERN = re.compile(r"^\d{6}$")


def email_valido(email: str) -> bool:
    return EMAIL_PATTERN.match(email) is not None


def clave_valida(clave: str) -> bool:
    return bool(clave) and PASSWORD_PATTERN.match(clave) is not None


def token_valido(token: str) -> bool:
    return TOKEN_PATTERN.match(token) is not None


def validar_login_form(email: str, clave: str) -> tuple[bool, str]:
    if not email.strip():
        return False, "El email es obligatorio."
    if not clave.strip():
        return False, "La clave es obligatoria."
    if not email_valido(email):
        return False, "El formato del email no es valido."
    if not clave_valida(clave):
        return False, "La clave solo puede contener letras, numeros y el caracter especial #."
    return True, ""


def validar_email_recuperacion(email: str) -> tuple[bool, str]:
    if not email.strip():
        return False, "El email es obligatorio."
    if not email_valido(email):
        return False, "El formato del email no es valido."
    return True, ""


def validar_nueva_clave(token: str, nueva_clave: str) -> tuple[bool, str]:
    if not token.strip():
        return False, "Debe digitar el token."
    if not token_valido(token):
        return False, "El token debe tener 6 digitos."
    if not nueva_clave.strip():
        return False, "Debe digitar la nueva clave."
    if not clave_valida(nueva_clave):
        return False, "La clave solo puede contener letras, numeros y el caracter especial #."
    return True, ""
