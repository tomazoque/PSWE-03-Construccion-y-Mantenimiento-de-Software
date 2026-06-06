from __future__ import annotations

from config import TOKEN_EXPIRATION_MINUTES, TOKEN_LOGIN_TYPE
from logic.auth_service import hash_password


def _user_row(password: str = "demo", active: bool = True):
    salt = b"1234567890abcdef"
    password_hash = hash_password(password, salt)
    return (1, "demo@fvncr.org", password_hash, salt, "Usuario Demo", "8888-8888", active)


def test_usuario_inexistente_produce_error_controlado(auth_service, repositories):
    user_repository, _token_repository, _email_service, audit_repository = repositories
    user_repository.find_by_email.return_value = None

    user = auth_service.authenticate("demo@fvncr.org", "demo")

    assert user is None
    audit_repository.record.assert_called_once_with(
        "LOGIN",
        "FALLIDO",
        email="demo@fvncr.org",
        message="Usuario inexistente.",
    )


def test_clave_incorrecta_produce_error_controlado(auth_service, repositories):
    user_repository, _token_repository, _email_service, audit_repository = repositories
    user_repository.find_by_email.return_value = _user_row(password="demo")

    user = auth_service.authenticate("demo@fvncr.org", "otra")

    assert user is None
    audit_repository.record.assert_called_once()
    assert audit_repository.record.call_args.args[:2] == ("LOGIN", "FALLIDO")
    assert audit_repository.record.call_args.kwargs["message"] == "Clave incorrecta."


def test_usuario_inactivo_produce_error_controlado(auth_service, repositories):
    user_repository, _token_repository, _email_service, audit_repository = repositories
    user_repository.find_by_email.return_value = _user_row(active=False)

    user = auth_service.authenticate("demo@fvncr.org", "demo")

    assert user is None
    assert audit_repository.record.call_args.args[:2] == ("LOGIN", "FALLIDO")
    assert audit_repository.record.call_args.kwargs["message"] == "Usuario inactivo."


def test_login_correcto_retorna_usuario_y_audita_exito(auth_service, repositories):
    user_repository, token_repository, email_service, audit_repository = repositories
    user_repository.find_by_email.return_value = _user_row(password="demo")

    user = auth_service.authenticate("demo@fvncr.org", "demo")

    assert user is not None
    assert user.id_usuario == 1
    assert user.email == "demo@fvncr.org"
    audit_repository.record.assert_called_once()
    assert audit_repository.record.call_args.args[:2] == ("LOGIN", "EXITOSO")
    token_repository.save.assert_not_called()
    email_service.send.assert_not_called()


def test_login_correcto_solicita_token_2fa(auth_service, repositories, monkeypatch):
    _user_repository, token_repository, email_service, _audit_repository = repositories
    monkeypatch.setattr("logic.auth_service.generate_token", lambda: "123456")
    user = _user_from_login(auth_service, repositories)

    auth_service.send_login_token(user)

    token_repository.save.assert_called_once_with(1, "123456", TOKEN_LOGIN_TYPE, TOKEN_EXPIRATION_MINUTES)
    email_service.send.assert_called_once()


def test_login_correcto_no_valida_2fa_automaticamente(auth_service, repositories):
    _user_repository, token_repository, _email_service, _audit_repository = repositories
    user = _user_from_login(auth_service, repositories)

    assert user is not None
    token_repository.consume.assert_not_called()


def _user_from_login(auth_service, repositories):
    user_repository, _token_repository, _email_service, _audit_repository = repositories
    user_repository.find_by_email.return_value = _user_row(password="demo")
    return auth_service.authenticate("demo@fvncr.org", "demo")
