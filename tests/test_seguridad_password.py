import secrets

from logic.auth_service import hash_password


def test_hash_no_es_igual_a_clave_en_plano():
    password = "Secret123"
    salt = secrets.token_bytes(16)
    h = hash_password(password, salt)
    assert isinstance(h, (bytes, bytearray))
    assert h != password.encode("utf-8")


def test_hashes_diferentes_con_salts_diferentes():
    password = "Secret123"
    salt1 = secrets.token_bytes(16)
    salt2 = secrets.token_bytes(16)
    h1 = hash_password(password, salt1)
    h2 = hash_password(password, salt2)
    assert h1 != h2


def test_verificacion_de_clave_correcta():
    password = "ClavePrueba"
    salt = secrets.token_bytes(16)
    h = hash_password(password, salt)
    # la verificación es comparar hashes
    assert hash_password(password, salt) == h


def test_salt_no_debe_ser_vacio():
    s = secrets.token_bytes(16)
    assert s and len(s) >= 16
