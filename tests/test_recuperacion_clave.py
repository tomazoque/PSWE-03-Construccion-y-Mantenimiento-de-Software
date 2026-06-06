from unittest.mock import Mock
import secrets

from logic.auth_service import AuthService, hash_password


def make_auth_service():
    user_repo = Mock()
    token_repo = Mock()
    email_service = Mock()
    audit_repo = Mock()
    svc = AuthService(user_repo, token_repo, email_service, audit_repo)
    return svc, user_repo, token_repo, email_service, audit_repo


def test_email_vacio_produce_error_validacion():
    from logic.validators import validar_email_recuperacion

    valido, _ = validar_email_recuperacion("")
    assert not valido


def test_email_inexistente_produce_error_controlado():
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    user_repo.find_by_email.return_value = None
    res = svc.request_password_recovery("no@x.com")
    assert res is None
    audit_repo.record.assert_called_with("RECUPERACION_CLAVE", "FALLIDO", email="no@x.com", message="Solicitud para usuario inexistente.")


def test_email_valido_genera_token_y_envia_correo(monkeypatch):
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    # user row: id, email, hash, salt, name, phone, active
    user_repo.find_by_email.return_value = (5, "r@x.com", b"h", b"s", "Nombre", None, True)
    # deterministic token
    monkeypatch.setattr('logic.auth_service.secrets', __import__('types').SimpleNamespace(randbelow=lambda x: 42))

    uid = svc.request_password_recovery("r@x.com")
    assert uid == 5
    assert token_repo.save.called
    assert email_service.send.called
    audit_repo.record.assert_called_with("RECUPERACION_CLAVE", "EXITOSO", email="r@x.com", user_id=5, message="Token de recuperación generado.")


def test_change_password_token_invalido_no_cambia():
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    token_repo.consume.return_value = False
    changed = svc.change_password(2, "000000", "Nueva1")
    assert not changed
    audit_repo.record.assert_called_with("CAMBIO_CLAVE", "FALLIDO", user_id=2, message="Token de recuperación inválido, expirado o usado.")


def test_change_password_token_valido_actualiza_clave():
    svc, user_repo, token_repo, email_service, audit_repo = make_auth_service()
    token_repo.consume.return_value = True
    changed = svc.change_password(3, "123456", "NuevaClave#")
    assert changed
    assert user_repo.update_password.called
    audit_repo.record.assert_called_with("CAMBIO_CLAVE", "EXITOSO", user_id=3, message="Clave actualizada correctamente.")
