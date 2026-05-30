"""
Punto de entrada de la aplicacion.

La funcionalidad esta separada en modulos para facilitar mantenimiento:
- config.py: variables de ambiente y constantes.
- database.py: conexion y errores de base de datos.
- repositories.py: consultas SQL.
- services.py: autenticacion, tokens y correo.
- validators.py: reglas de validacion.
- ui.py: interfaz Tkinter.
"""

from __future__ import annotations

from config import DatabaseConfig, SmtpConfig, configure_logging
from repositories import TokenRepository, UserRepository
from services import AuthService, EmailService
from ui import App


def create_app() -> App:
    db_config = DatabaseConfig()
    smtp_config = SmtpConfig()

    user_repository = UserRepository(db_config)
    token_repository = TokenRepository(db_config)
    email_service = EmailService(smtp_config)
    auth_service = AuthService(user_repository, token_repository, email_service)

    return App(auth_service)


if __name__ == "__main__":
    configure_logging()
    create_app().mainloop()
