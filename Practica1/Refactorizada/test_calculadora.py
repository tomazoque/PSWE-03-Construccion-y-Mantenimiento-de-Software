import pytest

from calculadora_pago import CalculadoraMatricula
from estudiante import Estudiante


def test_estudiante_nuevo_con_modalidad_virtual():
    estudiante = Estudiante("Ana", "nuevo", 1000, "virtual", False)
    calculadora = CalculadoraMatricula()

    total = calculadora.calcular(estudiante, mes=1)

    assert total == 925


def test_estudiante_regular_con_modalidad_presencial():
    estudiante = Estudiante("Luis", "regular", 1000, "presencial", False)
    calculadora = CalculadoraMatricula()

    total = calculadora.calcular(estudiante, mes=1)

    assert total == 1020


def test_estudiante_con_beca():
    estudiante = Estudiante("Maria", "regular", 1000, "virtual", True)
    calculadora = CalculadoraMatricula()

    total = calculadora.calcular(estudiante, mes=1)

    assert total == 745


def test_descuento_de_diciembre():
    estudiante = Estudiante("Carlos", "regular", 1000, "virtual", False)
    calculadora = CalculadoraMatricula()

    total = calculadora.calcular(estudiante, mes=12)

    assert total == 915


def test_total_nunca_menor_que_cero():
    estudiante = Estudiante("Sofia", "nuevo", 10, "virtual", True)
    calculadora = CalculadoraMatricula()

    total = calculadora.calcular(estudiante, mes=12)

    assert total == 0


def test_nombre_vacio_lanza_value_error():
    estudiante = Estudiante("", "nuevo", 1000, "virtual", False)
    calculadora = CalculadoraMatricula()

    with pytest.raises(ValueError, match="nombre no puede estar vacio"):
        calculadora.calcular(estudiante, mes=1)


def test_tipo_invalido_lanza_value_error():
    estudiante = Estudiante("Ana", "egresado", 1000, "virtual", False)
    calculadora = CalculadoraMatricula()

    with pytest.raises(ValueError, match="tipo debe ser 'nuevo' o 'regular'"):
        calculadora.calcular(estudiante, mes=1)


def test_modalidad_invalida_lanza_value_error():
    estudiante = Estudiante("Ana", "nuevo", 1000, "hibrida", False)
    calculadora = CalculadoraMatricula()

    with pytest.raises(ValueError, match="modalidad debe ser 'virtual' o 'presencial'"):
        calculadora.calcular(estudiante, mes=1)


def test_monto_negativo_lanza_value_error():
    estudiante = Estudiante("Ana", "nuevo", -100, "virtual", False)
    calculadora = CalculadoraMatricula()

    with pytest.raises(ValueError, match="monto no puede ser negativo"):
        calculadora.calcular(estudiante, mes=1)
