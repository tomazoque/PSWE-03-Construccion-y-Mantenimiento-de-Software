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
