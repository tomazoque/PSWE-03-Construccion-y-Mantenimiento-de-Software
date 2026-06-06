from __future__ import annotations

from config import TOKEN_EXPIRATION_MINUTES, TOKEN_LENGTH, TOKEN_LOGIN_TYPE
from logic.auth_service import generate_token
from logic.validators import token_valido
from models import User


def test_token_generado_no_esta_vacio():
    token = generate_token()

    assert token


def test_token_generado_tiene_longitud_esperada():
    token = generate_token()

    assert len(token) == TOKEN_LENGTH


def test_token_generado_es_numerico():
    token = generate_token()

    assert token.isdigit()


def test_generate_token_deterministico_con_mock(monkeypatch):
    monkeypatch.setattr("logic.auth_service.secrets.randbelow", lambda _maximum: 0)

    assert generate_token() == "100000"


def test_token_correcto_es_valido():
    assert token_valido("123456") is True


def test_token_incorrecto_es_rechazado():
    assert token_valido("ABC123") is False


def test_send_login_token_guarda_token_y_envia_email(auth_service, repositories, monkeypatch):
    _user_repository, token_repository, email_service, _audit_repository = repositories
    user = User(1, "demo@fvncr.org", "Usuario Demo", "8888-8888")
    monkeypatch.setattr("logic.auth_service.generate_token", lambda: "123456")

    auth_service.send_login_token(user)

    token_repository.save.assert_called_once_with(
        user.id_usuario,
        "123456",
        TOKEN_LOGIN_TYPE,
        TOKEN_EXPIRATION_MINUTES,
    )
    email_service.send.assert_called_once()
    assert "123456" in email_service.send.call_args.args[2]


def test_verify_login_token_correcto_retorna_true_y_audita(auth_service, repositories):
    _user_repository, token_repository, _email_service, audit_repository = repositories
    token_repository.consume.return_value = True
    user = User(1, "demo@fvncr.org", "Usuario Demo", "8888-8888")

    result = auth_service.verify_login_token(user, "123456")

    assert result is True
    token_repository.consume.assert_called_once_with(user.id_usuario, "123456", TOKEN_LOGIN_TYPE)
    audit_repository.record.assert_called_once()
    assert audit_repository.record.call_args.args[:2] == ("LOGIN_2FA", "EXITOSO")


def test_verify_login_token_incorrecto_retorna_false_y_audita(auth_service, repositories):
    _user_repository, token_repository, _email_service, audit_repository = repositories
    token_repository.consume.return_value = False
    user = User(1, "demo@fvncr.org", "Usuario Demo", "8888-8888")

    result = auth_service.verify_login_token(user, "999999")

    assert result is False
    audit_repository.record.assert_called_once()
    assert audit_repository.record.call_args.args[:2] == ("LOGIN_2FA", "FALLIDO")
