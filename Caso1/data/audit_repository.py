from __future__ import annotations

from config import DatabaseConfig
from data.database import get_connection


class AuditRepository:
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config

    def record(
        self,
        event: str,
        result: str,
        email: str | None = None,
        user_id: int | None = None,
        message: str | None = None,
    ) -> None:
        sql = """
        INSERT INTO dbo.AuditoriaLogin(id_usuario, email, evento, resultado, mensaje)
        VALUES (?, ?, ?, ?, ?)
        """
        with get_connection(self.db_config) as cn:
            cursor = cn.cursor()
            cursor.execute(sql, user_id, email, event, result, message)
            cn.commit()
