from __future__ import annotations

import hashlib
import secrets
from typing import Optional

from config import TOKEN_EXPIRATION_MINUTES, TOKEN_LENGTH, TOKEN_LOGIN_TYPE, TOKEN_RECOVERY_TYPE
from data import AuditRepository, TokenRepository, UserRepository
from models import User
from services.email_service import EmailService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        email_service: EmailService,
        audit_repository: AuditRepository,
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.email_service = email_service
        self.audit_repository = audit_repository

    def authenticate(self, email: str, password: str) -> Optional[User]:
        row = self.user_repository.find_by_email(email)
        if row is None:
            self.audit_repository.record("LOGIN", "FALLIDO", email=email, message="Usuario inexistente.")
            return None

        user_id, email_db, hash_db, salt_db, name, phone, active = row
        if not active:
            self.audit_repository.record(
                "LOGIN",
                "FALLIDO",
                email=email_db,
                user_id=user_id,
                message="Usuario inactivo.",
            )
            return None

        calculated_hash = hash_password(password, bytes(salt_db))
        if calculated_hash != bytes(hash_db):
            self.audit_repository.record(
                "LOGIN",
                "FALLIDO",
                email=email_db,
                user_id=user_id,
                message="Clave incorrecta.",
            )
            return None

        self.audit_repository.record(
            "LOGIN",
            "EXITOSO",
            email=email_db,
            user_id=user_id,
            message="Credenciales válidas.",
        )
        return User(user_id, email_db, name, phone)

    def send_login_token(self, user: User) -> None:
        token = generate_token()
        self.token_repository.save(user.id_usuario, token, TOKEN_LOGIN_TYPE, TOKEN_EXPIRATION_MINUTES)
        self.email_service.send(
            user.email,
            "Token de doble autenticación",
            (
                f"Hola {user.nombre}, su token de acceso es: {token}. "
                f"Expira en {TOKEN_EXPIRATION_MINUTES} minutos."
            ),
        )

    def verify_login_token(self, user: User, token: str) -> bool:
        is_valid = self.token_repository.consume(user.id_usuario, token, TOKEN_LOGIN_TYPE)
        self.audit_repository.record(
            "LOGIN_2FA",
            "EXITOSO" if is_valid else "FALLIDO",
            email=user.email,
            user_id=user.id_usuario,
            message="Token 2FA válido." if is_valid else "Token 2FA inválido, expirado o usado.",
        )
        return is_valid

    def request_password_recovery(self, email: str) -> Optional[int]:
        row = self.user_repository.find_by_email(email)
        if row is None:
            self.audit_repository.record(
                "RECUPERACION_CLAVE",
                "FALLIDO",
                email=email,
                message="Solicitud para usuario inexistente.",
            )
            return None

        user_id = row[0]
        name = row[4]
        token = generate_token()

        self.token_repository.save(user_id, token, TOKEN_RECOVERY_TYPE, TOKEN_EXPIRATION_MINUTES)
        self.email_service.send(
            email,
            "Token de recuperación de clave",
            (
                f"Hola {name}, su token de recuperación es: {token}. "
                f"Expira en {TOKEN_EXPIRATION_MINUTES} minutos."
            ),
        )
        self.audit_repository.record(
            "RECUPERACION_CLAVE",
            "EXITOSO",
            email=email,
            user_id=user_id,
            message="Token de recuperación generado.",
        )
        return user_id

    def change_password(self, user_id: int, token: str, new_password: str) -> bool:
        token_was_valid = self.token_repository.consume(user_id, token, TOKEN_RECOVERY_TYPE)
        if not token_was_valid:
            self.audit_repository.record(
                "CAMBIO_CLAVE",
                "FALLIDO",
                user_id=user_id,
                message="Token de recuperación inválido, expirado o usado.",
            )
            return False

        salt = secrets.token_bytes(16)
        password_hash = hash_password(new_password, salt)
        self.user_repository.update_password(user_id, password_hash, salt)
        self.audit_repository.record(
            "CAMBIO_CLAVE",
            "EXITOSO",
            user_id=user_id,
            message="Clave actualizada correctamente.",
        )
        return True

    def get_access_history(self, user: User):
        return self.audit_repository.find_access_history_by_user(user.id_usuario)

    def record_menu_access(self, user: User, option_name: str) -> None:
        self.audit_repository.record(
            "MENU",
            "EXITOSO",
            email=user.email,
            user_id=user.id_usuario,
            message=f"Opción consultada: {option_name}",
        )


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.sha256(salt + password.encode("utf-8")).digest()


def hash_clave(clave: str, salt: bytes) -> bytes:
    return hash_password(clave, salt)


def generate_token() -> str:
    minimum = 10 ** (TOKEN_LENGTH - 1)
    maximum = (10**TOKEN_LENGTH) - minimum
    return str(secrets.randbelow(maximum) + minimum)


def generar_token() -> str:
    return generate_token()
