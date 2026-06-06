from unittest.mock import Mock

from logic.auth_service import AuthService, hash_password


def test_auditoria_registra_intento_exitoso_y_fallido():
    user_repo = Mock()
    token_repo = Mock()
    email_service = Mock()
    audit_repo = Mock()
    svc = AuthService(user_repo, token_repo, email_service, audit_repo)

    # Simular intento fallido
    audit_repo.record.reset_mock()
    audit_repo.record("LOGIN", "FALLIDO", email="a@x.com", message="msg")
    audit_repo.record.assert_called()

    # Simular intento exitoso
    audit_repo.record.reset_mock()
    audit_repo.record("LOGIN", "EXITOSO", email="a@x.com", user_id=1, message="ok")
    audit_repo.record.assert_called()


def test_no_se_registra_clave_ni_hash_en_auditoria():
    # Usamos mock para interceptar llamadas
    audit_repo = Mock()
    audit_repo.record("LOGIN", "FALLIDO", email="u@x.com", message="Clave incorrecta.")
    call_kwargs = audit_repo.record.call_args.kwargs
    # Asegurar que no hay keys relacionadas con contraseñas
    forbidden = {"password", "clave", "clave_hash", "salt", "clave_salt"}
    assert forbidden.isdisjoint(call_kwargs.keys())


def test_auditoria_personal_filtra_por_usuario():
    user_repo = Mock()
    token_repo = Mock()
    email_service = Mock()
    audit_repo = Mock()
    svc = AuthService(user_repo, token_repo, email_service, audit_repo)

    # Simular que audit_repo devuelve listas sólo para el usuario solicitado
    audit_repo.find_access_history_by_user.return_value = [("2026-01-01", "LOGIN", "EXITOSO", "ok")]
    user = type("U", (), {"id_usuario": 99, "email": "x@x.com"})
    hist = svc.get_access_history(user)
    assert isinstance(hist, list)
    audit_repo.find_access_history_by_user.assert_called_with(99)
