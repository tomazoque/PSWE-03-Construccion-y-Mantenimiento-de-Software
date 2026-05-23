from decimal import Decimal

import pytest

from matricula import (
    MODALIDAD_PRESENCIAL,
    MODALIDAD_VIRTUAL,
    TIPO_NUEVO,
    TIPO_REGULAR,
    calcular_total_matricula,
    formatear_total_matricula,
    obtener_mes_actual,
)


def test_estudiante_nuevo_recibe_descuento_del_cinco_por_ciento():
    total = calcular_total_matricula(
        costo_base=1000,
        tipo_estudiante=TIPO_NUEVO,
        modalidad=MODALIDAD_VIRTUAL,
        mes=1,
    )

    assert total == Decimal("925.00")


def test_estudiante_regular_recibe_descuento_del_tres_por_ciento():
    total = calcular_total_matricula(
        costo_base=1000,
        tipo_estudiante=TIPO_REGULAR,
        modalidad=MODALIDAD_VIRTUAL,
        mes=1,
    )

    assert total == Decimal("945.00")


def test_beca_aplica_descuento_del_veinte_por_ciento():
    total = calcular_total_matricula(
        costo_base=1000,
        tipo_estudiante=TIPO_REGULAR,
        tiene_beca=True,
        modalidad=MODALIDAD_VIRTUAL,
        mes=1,
    )

    assert total == Decimal("745.00")


def test_modalidad_presencial_aplica_recargo_fijo():
    total = calcular_total_matricula(
        costo_base=1000,
        tipo_estudiante=TIPO_NUEVO,
        modalidad=MODALIDAD_PRESENCIAL,
        mes=1,
    )

    assert total == Decimal("1000.00")


def test_diciembre_aplica_descuento_fijo():
    total = calcular_total_matricula(
        costo_base=1000,
        tipo_estudiante=TIPO_REGULAR,
        modalidad=MODALIDAD_VIRTUAL,
        mes=12,
    )

    assert total == Decimal("915.00")


def test_total_nunca_es_menor_que_cero():
    total = calcular_total_matricula(
        costo_base=10,
        tipo_estudiante=TIPO_NUEVO,
        tiene_beca=True,
        modalidad=MODALIDAD_VIRTUAL,
        mes=12,
    )

    assert total == Decimal("0")


@pytest.mark.parametrize(
    "campo, valor, mensaje",
    [
        ("costo_base", -1, "costo_base no puede ser negativo"),
        ("tipo_estudiante", "egresado", "tipo_estudiante debe ser uno de"),
        ("tiene_beca", "si", "tiene_beca debe ser un valor booleano"),
        ("modalidad", "hibrida", "modalidad debe ser una de"),
        ("mes", 13, "mes debe estar entre 1 y 12"),
    ],
)
def test_valida_entradas_invalidas(campo, valor, mensaje):
    datos_validos = {
        "costo_base": 1000,
        "tipo_estudiante": TIPO_NUEVO,
        "tiene_beca": False,
        "modalidad": MODALIDAD_VIRTUAL,
        "mes": 1,
    }
    datos_validos[campo] = valor

    with pytest.raises(ValueError, match=mensaje):
        calcular_total_matricula(**datos_validos)


def test_formateo_del_total_esta_separado_del_calculo():
    assert formatear_total_matricula(Decimal("925")) == "Total de matricula: 925.00"


def test_obtener_mes_actual_permite_inyectar_reloj():
    class RelojFalso:
        month = 12

    assert obtener_mes_actual(lambda: RelojFalso()) == 12
