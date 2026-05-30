from __future__ import annotations

from config import DatabaseConfig
from data.database import get_connection


class TokenRepository:
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config

    def save(self, user_id: int, token: str, token_type: str, minutes: int) -> None:
        sql = """
        INSERT INTO dbo.Token2FA(id_usuario, token, tipo, fecha_expira, usado)
        VALUES (?, ?, ?, DATEADD(MINUTE, ?, SYSDATETIME()), 0)
        """
        with get_connection(self.db_config) as cn:
            cursor = cn.cursor()
            cursor.execute(sql, user_id, token, token_type, minutes)
            cn.commit()

    def consume(self, user_id: int, token: str, token_type: str) -> bool:
        sql_find = """
        SELECT TOP 1 id_token
        FROM dbo.Token2FA
        WHERE id_usuario = ?
          AND token = ?
          AND tipo = ?
          AND usado = 0
          AND fecha_expira >= SYSDATETIME()
        ORDER BY fecha_creacion DESC
        """
        sql_update = """
        UPDATE dbo.Token2FA
        SET usado = 1
        WHERE id_token = ?
        """

        with get_connection(self.db_config) as cn:
            cursor = cn.cursor()
            cursor.execute(sql_find, user_id, token, token_type)
            row = cursor.fetchone()

            if row is None:
                return False

            cursor.execute(sql_update, row[0])
            cn.commit()
            return True
