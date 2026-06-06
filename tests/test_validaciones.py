import pytest

from logic import validators


def test_email_vacio_es_invalido():
    valido, _ = validators.validar_login_form("", "clave")
    assert not valido


def test_email_sin_arroba_es_invalido():
    assert not validators.email_valido("abc")


def test_email_sin_dominio_es_invalido():
    assert not validators.email_valido("usuario@")


def test_email_formato_correcto_es_valido():
    assert validators.email_valido("usuario@dominio.com")


def test_email_con_espacios_se_comporta_segun_logica_actual():
    # Según la implementación actual, email_valido no aplica strip(), por tanto
    # un email con espacios al inicio/fin es inválido.
    assert not validators.email_valido(" demo@fvncr.org ")


def test_clave_vacia_es_invalida():
    assert not validators.clave_valida("")


def test_clave_con_caracter_no_permitido_es_invalida():
    assert not validators.clave_valida("demo*")


def test_clave_valida_es_aceptada():
    assert validators.clave_valida("demo")
    assert validators.clave_valida("Demo123")


def test_clave_con_espacios_es_invalida():
    assert not validators.clave_valida(" demo ")
