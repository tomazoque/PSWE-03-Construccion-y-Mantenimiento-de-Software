from __future__ import annotations

from config import DatabaseConfig
from data.audit_repository import AuditRepository
from models import User


class FakeCursor:
    def __init__(self):
        self.calls = []
        self.rows = [("2026-06-05 18:00:00", "LOGIN", "EXITOSO", "Credenciales válidas.")]

    def execute(self, sql, *params):
        self.calls.append((sql, params))

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True


def test_auditoria_registra_intento_exitoso_sin_datos_sensibles(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr("data.audit_repository.get_connection", lambda _config: connection)
    repository = AuditRepository(DatabaseConfig())

    repository.record("LOGIN", "EXITOSO", email="demo@fvncr.org", user_id=1, message="Credenciales válidas.")

    sql, params = connection.cursor_instance.calls[0]
    assert "INSERT INTO dbo.AuditoriaLogin" in sql
    assert params == (1, "demo@fvncr.org", "LOGIN", "EXITOSO", "Credenciales válidas.")
    assert connection.committed is True
    _assert_no_sensitive_values(params)


def test_auditoria_registra_intento_fallido_sin_datos_sensibles(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr("data.audit_repository.get_connection", lambda _config: connection)
    repository = AuditRepository(DatabaseConfig())

    repository.record("LOGIN", "FALLIDO", email="demo@fvncr.org", user_id=1, message="Clave incorrecta.")

    _sql, params = connection.cursor_instance.calls[0]
    assert params == (1, "demo@fvncr.org", "LOGIN", "FALLIDO", "Clave incorrecta.")
    _assert_no_sensitive_values(params)


def test_auditoria_personal_filtra_por_usuario_autenticado(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr("data.audit_repository.get_connection", lambda _config: connection)
    repository = AuditRepository(DatabaseConfig())

    rows = repository.find_access_history_by_user(user_id=7, limit=50)

    sql, params = connection.cursor_instance.calls[0]
    assert rows == connection.cursor_instance.rows
    assert "FROM dbo.AuditoriaLogin" in sql
    assert "WHERE id_usuario = ?" in sql
    assert "ORDER BY fecha_evento DESC" in sql
    assert params == (50, 7)


def test_auditoria_personal_usa_id_del_usuario_actual(auth_service, repositories):
    _user_repository, _token_repository, _email_service, audit_repository = repositories
    audit_repository.find_access_history_by_user.return_value = [("fecha", "LOGIN", "EXITOSO", "OK")]
    current_user = User(9, "actual@fvncr.org", "Actual", None)

    rows = auth_service.get_access_history(current_user)

    assert rows == [("fecha", "LOGIN", "EXITOSO", "OK")]
    audit_repository.find_access_history_by_user.assert_called_once_with(9)


def test_auditoria_menu_registra_usuario_autenticado(auth_service, repositories):
    _user_repository, _token_repository, _email_service, audit_repository = repositories
    current_user = User(9, "actual@fvncr.org", "Actual", None)

    auth_service.record_menu_access(current_user, "Opción 1")

    audit_repository.record.assert_called_once_with(
        "MENU",
        "EXITOSO",
        email="actual@fvncr.org",
        user_id=9,
        message="Opción consultada: Opción 1",
    )


def _assert_no_sensitive_values(params):
    joined = " ".join("" if value is None else str(value).lower() for value in params)
    assert "password" not in joined
    assert "hash" not in joined
    assert "salt" not in joined
    assert "token" not in joined
