from __future__ import annotations

import secrets

from logic.auth_service import hash_clave, hash_password


def test_password_se_hashea_como_bytes_sha256():
    salt = b"1234567890abcdef"

    password_hash = hash_password("demo", salt)

    assert isinstance(password_hash, bytes)
    assert len(password_hash) == 32


def test_hash_no_es_igual_a_password_en_texto_plano():
    salt = b"1234567890abcdef"

    password_hash = hash_password("demo", salt)

    assert password_hash != b"demo"
    assert password_hash != "demo"


def test_misma_password_con_salts_distintos_genera_hashes_distintos():
    first_hash = hash_password("demo", b"1111111111111111")
    second_hash = hash_password("demo", b"2222222222222222")

    assert first_hash != second_hash


def test_password_correcta_coincide_al_recalcular_hash():
    salt = b"1234567890abcdef"
    stored_hash = hash_password("demo", salt)

    assert hash_password("demo", salt) == stored_hash


def test_password_incorrecta_no_coincide_al_recalcular_hash():
    salt = b"1234567890abcdef"
    stored_hash = hash_password("demo", salt)

    assert hash_password("otra", salt) != stored_hash


def test_salt_aleatorio_no_es_vacio():
    salt = secrets.token_bytes(16)

    assert salt
    assert len(salt) == 16


def test_alias_hash_clave_mantiene_mismo_resultado():
    salt = b"1234567890abcdef"

    assert hash_clave("demo", salt) == hash_password("demo", salt)
