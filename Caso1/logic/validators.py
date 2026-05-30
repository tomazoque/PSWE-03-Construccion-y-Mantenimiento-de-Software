from __future__ import annotations

import re


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PASSWORD_PATTERN = re.compile(r"^[A-Za-z0-9#]+$")
TOKEN_PATTERN = re.compile(r"^\d{6}$")
CELLPHONE_PATTERN = re.compile(r"^\d{4}-\d{4}$")


def email_valido(email: str) -> bool:
    return EMAIL_PATTERN.match(email) is not None


def clave_valida(clave: str) -> bool:
    return bool(clave) and PASSWORD_PATTERN.match(clave) is not None


def token_valido(token: str) -> bool:
    return TOKEN_PATTERN.match(token) is not None


def celular_valido(celular: str) -> bool:
    return CELLPHONE_PATTERN.match(celular) is not None


def validar_login_form(email: str, clave: str) -> tuple[bool, str]:
    if not email.strip():
        return False, "El email es obligatorio."
    if not clave.strip():
        return False, "La clave es obligatoria."
    if not email_valido(email):
        return False, "El formato del email no es válido."
    if not clave_valida(clave):
        return False, "La clave solo puede contener letras, números y el carácter especial #."
    return True, ""


def validar_email_recuperacion(email: str) -> tuple[bool, str]:
    if not email.strip():
        return False, "El email es obligatorio."
    if not email_valido(email):
        return False, "El formato del email no es válido."
    return True, ""


def validar_nueva_clave(token: str, nueva_clave: str) -> tuple[bool, str]:
    if not token.strip():
        return False, "Debe digitar el token."
    if not token_valido(token):
        return False, "El token debe tener 6 dígitos."
    if not nueva_clave.strip():
        return False, "Debe digitar la nueva clave."
    if not clave_valida(nueva_clave):
        return False, "La clave solo puede contener letras, números y el carácter especial #."
    return True, ""


def validar_registro_usuario(
    nombre: str,
    email: str,
    celular: str,
    clave: str,
    confirmar_clave: str,
) -> tuple[bool, str]:
    if not nombre.strip():
        return False, "El nombre es obligatorio."
    if not email.strip():
        return False, "El email es obligatorio."
    if not email_valido(email):
        return False, "El formato del email no es válido."
    if not celular.strip():
        return False, "El celular es obligatorio."
    if not celular_valido(celular):
        return False, "El celular debe tener el formato ####-####. Ejemplo: 8888-8888."
    if not clave.strip():
        return False, "La clave es obligatoria."
    if not clave_valida(clave):
        return False, "La clave solo puede contener letras, números y el carácter especial #."
    if not confirmar_clave.strip():
        return False, "Debe confirmar la clave."
    if clave != confirmar_clave:
        return False, "La confirmación de clave no coincide."
    return True, ""
