from __future__ import annotations

from config import DatabaseConfig
from data.database import get_connection


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

    def create(self, email: str, password_hash: bytes, salt: bytes, name: str, phone: str | None) -> int:
        sql = """
        INSERT INTO dbo.Usuario(email, clave_hash, clave_salt, nombre, celular, activo)
        OUTPUT INSERTED.id_usuario
        VALUES (?, ?, ?, ?, ?, 1)
        """
        with get_connection(self.db_config) as cn:
            cursor = cn.cursor()
            cursor.execute(sql, email, password_hash, salt, name, phone)
            user_id = cursor.fetchone()[0]
            cn.commit()
            return user_id

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
