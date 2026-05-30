from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional


TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES", "5"))
TOKEN_LOGIN_TYPE = "LOGIN_2FA"
TOKEN_RECOVERY_TYPE = "RECUPERACION"
TOKEN_LENGTH = 6


def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


@dataclass(frozen=True)
class DatabaseConfig:
    server: str = os.getenv("DB_SERVER", "localhost")
    name: str = os.getenv("DB_NAME", "CMSoftwareDemo")
    driver: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    user: Optional[str] = os.getenv("DB_USER")
    password: Optional[str] = os.getenv("DB_PASSWORD")

    @property
    def connection_string(self) -> str:
        base = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.name};"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )

        if self.user and self.password:
            return f"{base}UID={self.user};PWD={self.password};"

        return f"{base}Trusted_Connection=yes;"


@dataclass(frozen=True)
class SmtpConfig:
    server: Optional[str] = os.getenv("SMTP_SERVER")
    port: int = int(os.getenv("SMTP_PORT", "587"))
    user: Optional[str] = os.getenv("SMTP_USER")
    password: Optional[str] = os.getenv("SMTP_PASSWORD")
    sender: Optional[str] = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")

    @property
    def configured(self) -> bool:
        return bool(self.server and self.user and self.password and self.sender)
