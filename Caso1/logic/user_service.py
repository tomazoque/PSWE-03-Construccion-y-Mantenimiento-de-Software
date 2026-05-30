from __future__ import annotations

import secrets

from data import AuditRepository, UserRepository
from logic.auth_service import hash_password
from models import User


class UserService:
    def __init__(self, user_repository: UserRepository, audit_repository: AuditRepository):
        self.user_repository = user_repository
        self.audit_repository = audit_repository

    def email_exists(self, email: str) -> bool:
        return self.user_repository.find_by_email(email) is not None

    def register_user(self, nombre: str, email: str, celular: str, clave: str) -> User | None:
        if self.email_exists(email):
            self.audit_repository.record(
                "REGISTRO_USUARIO",
                "FALLIDO",
                email=email,
                message="El email ya existe.",
            )
            return None

        salt = secrets.token_bytes(16)
        password_hash = hash_password(clave, salt)
        phone = celular.strip() or None
        user_id = self.user_repository.create(email, password_hash, salt, nombre.strip(), phone)
        self.audit_repository.record(
            "REGISTRO_USUARIO",
            "EXITOSO",
            email=email,
            user_id=user_id,
            message="Usuario registrado correctamente.",
        )
        return User(user_id, email, nombre.strip(), phone)
