import secrets

from logic import validators
from logic import auth_service
from config import TOKEN_LENGTH


def test_generate_token_no_vacio(monkeypatch):
    # Hacemos determinista randbelow
    monkeypatch.setattr(auth_service.secrets, "randbelow", lambda x: 12345)
    token = auth_service.generate_token()
    assert token
    assert len(token) == TOKEN_LENGTH
    assert token.isdigit()


def test_token_valido_segun_patron():
    assert validators.token_valido("123456")
    assert not validators.token_valido("abc123")
