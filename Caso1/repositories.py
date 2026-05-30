from __future__ import annotations

from config import DatabaseConfig
from database import get_connection


class UserRepository:
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config

    def find_by_email(self, email: str):
        sql = """
        SELECT id_usuario, email, clave_hash, clave_salt, nombre, celular, activo
        FROM dbo.Usuario
        WHERE email = ?
        """
        with get_connection(self.db_config) as cn:
            cursor = cn.cursor()
            cursor.execute(sql, email)
            return cursor.fetchone()

    def update_password(self, user_id: int, password_hash: bytes, salt: bytes) -> None:
        sql = """
        UPDATE dbo.Usuario
        SET clave_hash = ?, clave_salt = ?
        WHERE id_usuario = ?
        """
        with get_connection(self.db_config) as cn:
            cursor = cn.cursor()
            cursor.execute(sql, password_hash, salt, user_id)
            cn.commit()


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
