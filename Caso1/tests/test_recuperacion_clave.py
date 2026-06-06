from __future__ import annotations

from config import TOKEN_EXPIRATION_MINUTES, TOKEN_RECOVERY_TYPE
from logic.validators import validar_email_recuperacion, validar_nueva_clave


def _user_row():
    return (1, "demo@fvncr.org", b"hash", b"salt", "Usuario Demo", "8888-8888", True)


def test_recuperacion_email_vacio_produce_error():
    is_valid, message = validar_email_recuperacion("")

    assert is_valid is False
    assert message == "El email es obligatorio."


def test_recuperacion_email_invalido_produce_error():
    is_valid, message = validar_email_recuperacion("demo")

    assert is_valid is False
    assert "email" in message.lower()


def test_recuperacion_email_inexistente_retorna_none_y_audita(auth_service, repositories):
    user_repository, _token_repository, _email_service, audit_repository = repositories
    user_repository.find_by_email.return_value = None

    user_id = auth_service.request_password_recovery("demo@fvncr.org")

    assert user_id is None
    audit_repository.record.assert_called_once()
    assert audit_repository.record.call_args.args[:2] == ("RECUPERACION_CLAVE", "FALLIDO")


def test_recuperacion_email_valido_genera_token_y_envia_correo(auth_service, repositories, monkeypatch):
    user_repository, token_repository, email_service, audit_repository = repositories
    user_repository.find_by_email.return_value = _user_row()
    monkeypatch.setattr("logic.auth_service.generate_token", lambda: "654321")

    user_id = auth_service.request_password_recovery("demo@fvncr.org")

    assert user_id == 1
    token_repository.save.assert_called_once_with(1, "654321", TOKEN_RECOVERY_TYPE, TOKEN_EXPIRATION_MINUTES)
    email_service.send.assert_called_once()
    assert "654321" in email_service.send.call_args.args[2]
    assert audit_repository.record.call_args.args[:2] == ("RECUPERACION_CLAVE", "EXITOSO")


def test_token_incorrecto_rechaza_cambio_de_clave(auth_service, repositories):
    _user_repository, token_repository, _email_service, audit_repository = repositories
    token_repository.consume.return_value = False

    result = auth_service.change_password(1, "999999", "Demo123")

    assert result is False
    token_repository.consume.assert_called_once()
    auth_service.user_repository.update_password.assert_not_called()
    assert audit_repository.record.call_args.args[:2] == ("CAMBIO_CLAVE", "FALLIDO")


def test_nueva_clave_invalida_produce_error():
    is_valid, message = validar_nueva_clave("123456", "Demo*")

    assert is_valid is False
    assert "clave" in message.lower()


def test_token_correcto_actualiza_clave_con_hash_y_salt(auth_service, repositories, monkeypatch):
    user_repository, token_repository, _email_service, audit_repository = repositories
    token_repository.consume.return_value = True
    monkeypatch.setattr("logic.auth_service.secrets.token_bytes", lambda size: b"A" * size)

    result = auth_service.change_password(1, "123456", "Demo123")

    assert result is True
    user_repository.update_password.assert_called_once()
    user_id, password_hash, salt = user_repository.update_password.call_args.args
    assert user_id == 1
    assert isinstance(password_hash, bytes)
    assert password_hash != b"Demo123"
    assert salt == b"A" * 16
    assert audit_repository.record.call_args.args[:2] == ("CAMBIO_CLAVE", "EXITOSO")
