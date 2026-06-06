from __future__ import annotations

import pytest

from logic.validators import (
    clave_valida,
    email_valido,
    token_valido,
    validar_email_recuperacion,
    validar_login_form,
    validar_nueva_clave,
)


@pytest.mark.parametrize("email", ["", "abc", "usuario@"])
def test_email_invalido_por_formato(email):
    assert email_valido(email) is False


def test_email_con_formato_correcto_es_valido():
    assert email_valido("usuario@dominio.com") is True


def test_email_con_espacios_extra_es_invalido_en_validador_puro():
    assert email_valido(" demo@fvncr.org ") is False


def test_login_form_con_email_y_clave_limpios_es_valido():
    assert validar_login_form("demo@fvncr.org", "demo") == (True, "")


def test_login_form_email_vacio_produce_error():
    is_valid, message = validar_login_form("", "demo")

    assert is_valid is False
    assert message == "El email es obligatorio."


def test_login_form_clave_vacia_produce_error():
    is_valid, message = validar_login_form("demo@fvncr.org", "")

    assert is_valid is False
    assert message == "La clave es obligatoria."


def test_login_form_email_invalido_produce_error():
    is_valid, message = validar_login_form("abc", "demo")

    assert is_valid is False
    assert "email" in message.lower()


def test_login_form_clave_con_caracter_no_permitido_produce_error():
    is_valid, message = validar_login_form("demo@fvncr.org", "demo*")

    assert is_valid is False
    assert "clave" in message.lower()


@pytest.mark.parametrize("clave", ["", "demo*", " demo "])
def test_clave_invalida(clave):
    assert clave_valida(clave) is False


@pytest.mark.parametrize("clave", ["demo", "Demo123", "Demo#123"])
def test_clave_valida(clave):
    assert clave_valida(clave) is True


@pytest.mark.parametrize("token", ["", "12345", "abcdef", "1234567"])
def test_token_invalido(token):
    assert token_valido(token) is False


def test_token_de_seis_digitos_es_valido():
    assert token_valido("123456") is True


def test_validar_email_recuperacion_rechaza_email_vacio():
    is_valid, message = validar_email_recuperacion("")

    assert is_valid is False
    assert message == "El email es obligatorio."


def test_validar_email_recuperacion_rechaza_email_invalido():
    is_valid, message = validar_email_recuperacion("usuario")

    assert is_valid is False
    assert "email" in message.lower()


def test_validar_nueva_clave_rechaza_token_invalido():
    is_valid, message = validar_nueva_clave("123", "Demo123")

    assert is_valid is False
    assert "token" in message.lower()


def test_validar_nueva_clave_rechaza_clave_invalida():
    is_valid, message = validar_nueva_clave("123456", "Demo*")

    assert is_valid is False
    assert "clave" in message.lower()
