from unittest.mock import Mock
import secrets

from logic.auth_service import AuthService, hash_password
from logic.validators import validar_login_form


def make_auth_service():
    user_repo = Mock()
    token_repo = Mock()
    email_service = Mock()
    audit_repo = Mock()
    svc = AuthService(user_repo, token_repo, email_service, audit_repo)
    return svc, user_repo, token_repo, email_service, audit_repo


def test_email_vacio_produce_error_validacion():
    valido, _ = validar_login_form("", "clave")
    assert not valido


def test_usuario_inexistente_produce_error_y_auditoria():
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    user_repo.find_by_email.return_value = None
    res = svc.authenticate("noex@x.com", "any")
    assert res is None
    audit_repo.record.assert_called_with("LOGIN", "FALLIDO", email="noex@x.com", message="Usuario inexistente.")


def test_clave_incorrecta_produce_error_y_auditoria():
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    salt = secrets.token_bytes(16)
    # store hash of 'correct'
    hash_db = hash_password("correct", salt)
    user_row = (1, "u@x.com", hash_db, salt, "Name", "8888-8888", True)
    user_repo.find_by_email.return_value = user_row
    res = svc.authenticate("u@x.com", "wrong")
    assert res is None
    audit_repo.record.assert_called_with("LOGIN", "FALLIDO", email="u@x.com", user_id=1, message="Clave incorrecta.")


def test_login_correcto_solicita_token_2fa(monkeypatch):
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    salt = secrets.token_bytes(16)
    password = "MiClave123"
    hash_db = hash_password(password, salt)
    user_row = (42, "ok@x.com", hash_db, salt, "Nombre", "8888-8888", True)
    user_repo.find_by_email.return_value = user_row

    user = svc.authenticate("ok@x.com", password)
    assert user is not None
    # Ensure login success audit recorded
    audit_repo.record.assert_any_call("LOGIN", "EXITOSO", email="ok@x.com", user_id=42, message="Credenciales válidas.")

    # Make token deterministic
    monkeypatch.setattr(svc, "token_repository", token_repo)
    monkeypatch.setattr(svc, "email_service", email_service)
    monkeypatch.setattr('logic.auth_service.secrets', __import__('types').SimpleNamespace(randbelow=lambda x: 1))

    svc.send_login_token(user)
    # token_repo.save should be called
    assert token_repo.save.called
    assert email_service.send.called
    # No menu access should be recorded at this point
    for call in audit_repo.record.call_args_list:
        assert call[0][0] != "MENU"


def test_usuario_inactivo_no_authenticado():
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    salt = secrets.token_bytes(16)
    hash_db = hash_password("p", salt)
    user_row = (7, "inactive@x.com", hash_db, salt, "Nombre", "8888-8888", False)
    user_repo.find_by_email.return_value = user_row
    res = svc.authenticate("inactive@x.com", "p")
    assert res is None
    audit_repo.record.assert_called_with("LOGIN", "FALLIDO", email="inactive@x.com", user_id=7, message="Usuario inactivo.")
