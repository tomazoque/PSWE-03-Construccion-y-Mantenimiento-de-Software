from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from config import SmtpConfig


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

        smtp_server = self.smtp_config.server
        smtp_user = self.smtp_config.user
        smtp_password = self.smtp_config.password
        smtp_sender = self.smtp_config.sender
        if smtp_server is None or smtp_user is None or smtp_password is None or smtp_sender is None:
            # Defensive check: configured=True should guarantee all values are present.
            raise ValueError("La configuración SMTP está incompleta.")

        message = EmailMessage()
        message["From"] = smtp_sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        context = ssl.create_default_context()
        if hasattr(ssl, "TLSVersion"):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            # Backward-compatible hardening para builds antiguos de Python/OpenSSL que no soportan TLSv1.2+ por defecto.
            context.options |= getattr(ssl, "OP_NO_SSLv2", 0)
            context.options |= getattr(ssl, "OP_NO_SSLv3", 0)
            context.options |= getattr(ssl, "OP_NO_TLSv1", 0)
            context.options |= getattr(ssl, "OP_NO_TLSv1_1", 0)

        with smtplib.SMTP(smtp_server, self.smtp_config.port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(message)
