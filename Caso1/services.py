from __future__ import annotations

import hashlib
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from config import (
    SmtpConfig,
    TOKEN_EXPIRATION_MINUTES,
    TOKEN_LENGTH,
    TOKEN_LOGIN_TYPE,
    TOKEN_RECOVERY_TYPE,
)
from models import User
from repositories import TokenRepository, UserRepository


class EmailService:
    def __init__(self, smtp_config: SmtpConfig):
        self.smtp_config = smtp_config

    def send(self, recipient: str, subject: str, body: str) -> None:
        if not self.smtp_config.configured:
            print("\n=== MODO DEMO: EMAIL NO CONFIGURADO ===")
            print(f"Para: {recipient}")
            print(f"Asunto: {subject}")
            print(body)
            print("======================================\n")
            return

        message = EmailMessage()
        message["From"] = self.smtp_config.sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP(self.smtp_config.server, self.smtp_config.port) as server:
            server.starttls(context=context)
            server.login(self.smtp_config.user, self.smtp_config.password)
            server.send_message(message)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.email_service = email_service

    def authenticate(self, email: str, password: str) -> Optional[User]:
        row = self.user_repository.find_by_email(email)
        if row is None:
            return None

        user_id, email_db, hash_db, salt_db, name, phone, active = row
        if not active:
            return None

        calculated_hash = hash_password(password, bytes(salt_db))
        if calculated_hash != bytes(hash_db):
            return None

        return User(user_id, email_db, name, phone)

    def send_login_token(self, user: User) -> None:
        token = generate_token()
        self.token_repository.save(
            user.id_usuario,
            token,
            TOKEN_LOGIN_TYPE,
            TOKEN_EXPIRATION_MINUTES,
        )
        self.email_service.send(
            user.email,
            "Token de doble autenticacion",
            (
                f"Hola {user.nombre}, su token de acceso es: {token}. "
                f"Expira en {TOKEN_EXPIRATION_MINUTES} minutos."
            ),
        )

    def verify_login_token(self, user: User, token: str) -> bool:
        return self.token_repository.consume(user.id_usuario, token, TOKEN_LOGIN_TYPE)

    def request_password_recovery(self, email: str) -> Optional[int]:
        row = self.user_repository.find_by_email(email)
        if row is None:
            return None

        user_id = row[0]
        name = row[4]
        token = generate_token()

        self.token_repository.save(
            user_id,
            token,
            TOKEN_RECOVERY_TYPE,
            TOKEN_EXPIRATION_MINUTES,
        )
        self.email_service.send(
            email,
            "Token de recuperacion de clave",
            (
                f"Hola {name}, su token de recuperacion es: {token}. "
                f"Expira en {TOKEN_EXPIRATION_MINUTES} minutos."
            ),
        )
        return user_id

    def change_password(self, user_id: int, token: str, new_password: str) -> bool:
        token_was_valid = self.token_repository.consume(
            user_id,
            token,
            TOKEN_RECOVERY_TYPE,
        )
        if not token_was_valid:
            return False

        salt = secrets.token_bytes(16)
        password_hash = hash_password(new_password, salt)
        self.user_repository.update_password(user_id, password_hash, salt)
        return True


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
