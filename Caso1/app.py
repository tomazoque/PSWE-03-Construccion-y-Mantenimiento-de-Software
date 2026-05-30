"""Punto de entrada de la aplicación."""

from __future__ import annotations

from config import DatabaseConfig, SmtpConfig, configure_logging
from data import AuditRepository, TokenRepository, UserRepository
from logic import AuthService, UserService
from services import EmailService
from ui import App


def create_app() -> App:
    db_config = DatabaseConfig()
    smtp_config = SmtpConfig()

    user_repository = UserRepository(db_config)
    token_repository = TokenRepository(db_config)
    audit_repository = AuditRepository(db_config)
    email_service = EmailService(smtp_config)
    auth_service = AuthService(user_repository, token_repository, email_service, audit_repository)
    user_service = UserService(user_repository, audit_repository)

    return App(auth_service, user_service)


if __name__ == "__main__":
    configure_logging()
    create_app().mainloop()
