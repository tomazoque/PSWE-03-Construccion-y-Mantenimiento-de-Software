from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


TIPO_NUEVO = "nuevo"
TIPO_REGULAR = "regular"
TIPOS_ESTUDIANTE_VALIDOS = {TIPO_NUEVO, TIPO_REGULAR}

MODALIDAD_VIRTUAL = "virtual"
MODALIDAD_PRESENCIAL = "presencial"
MODALIDADES_VALIDAS = {MODALIDAD_VIRTUAL, MODALIDAD_PRESENCIAL}

DESCUENTO_ESTUDIANTE_NUEVO = Decimal("0.05")
DESCUENTO_ESTUDIANTE_REGULAR = Decimal("0.03")
DESCUENTO_BECA = Decimal("0.20")
DESCUENTO_MODALIDAD_VIRTUAL = Decimal("25")
RECARGO_MODALIDAD_PRESENCIAL = Decimal("50")
DESCUENTO_DICIEMBRE = Decimal("30")

MES_DICIEMBRE = 12
TOTAL_MINIMO = Decimal("0")


@dataclass(frozen=True)
class DatosMatricula:
    costo_base: Decimal
    tipo_estudiante: str
    tiene_beca: bool
    modalidad: str
    mes: int


def calcular_total_matricula(
    costo_base,
    tipo_estudiante,
    tiene_beca=False,
    modalidad=MODALIDAD_PRESENCIAL,
    mes=None,
):
    datos = validar_datos_matricula(
        costo_base=costo_base,
        tipo_estudiante=tipo_estudiante,
        tiene_beca=tiene_beca,
        modalidad=modalidad,
        mes=mes,
    )

    total = datos.costo_base
    total -= calcular_descuento_por_tipo(datos.costo_base, datos.tipo_estudiante)

    if datos.tiene_beca:
        total -= datos.costo_base * DESCUENTO_BECA

    total += calcular_ajuste_por_modalidad(datos.modalidad)

    if es_diciembre(datos.mes):
        total -= DESCUENTO_DICIEMBRE

    return max(total, TOTAL_MINIMO)


def validar_datos_matricula(costo_base, tipo_estudiante, tiene_beca, modalidad, mes):
    costo = convertir_a_decimal(costo_base, "costo_base")
    if costo < TOTAL_MINIMO:
        raise ValueError("El costo_base no puede ser negativo.")

    tipo_normalizado = normalizar_texto(tipo_estudiante, "tipo_estudiante")
    if tipo_normalizado not in TIPOS_ESTUDIANTE_VALIDOS:
        raise ValueError(
            f"tipo_estudiante debe ser uno de: {', '.join(sorted(TIPOS_ESTUDIANTE_VALIDOS))}."
        )

    if not isinstance(tiene_beca, bool):
        raise ValueError("tiene_beca debe ser un valor booleano.")

    modalidad_normalizada = normalizar_texto(modalidad, "modalidad")
    if modalidad_normalizada not in MODALIDADES_VALIDAS:
        raise ValueError(
            f"modalidad debe ser una de: {', '.join(sorted(MODALIDADES_VALIDAS))}."
        )

    mes_validado = validar_mes(mes)

    return DatosMatricula(
        costo_base=costo,
        tipo_estudiante=tipo_normalizado,
        tiene_beca=tiene_beca,
        modalidad=modalidad_normalizada,
        mes=mes_validado,
    )


def convertir_a_decimal(valor, nombre_campo):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{nombre_campo} debe ser un numero valido.") from None


def normalizar_texto(valor, nombre_campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nombre_campo} debe ser texto no vacio.")

    return valor.strip().lower()


def validar_mes(mes):
    if not isinstance(mes, int):
        raise ValueError("mes debe ser un numero entero.")

    if mes < 1 or mes > 12:
        raise ValueError("mes debe estar entre 1 y 12.")

    return mes


def calcular_descuento_por_tipo(costo_base, tipo_estudiante):
    descuentos = {
        TIPO_NUEVO: DESCUENTO_ESTUDIANTE_NUEVO,
        TIPO_REGULAR: DESCUENTO_ESTUDIANTE_REGULAR,
    }
    return costo_base * descuentos[tipo_estudiante]


def calcular_ajuste_por_modalidad(modalidad):
    if modalidad == MODALIDAD_VIRTUAL:
        return -DESCUENTO_MODALIDAD_VIRTUAL

    return RECARGO_MODALIDAD_PRESENCIAL


def es_diciembre(mes):
    return mes == MES_DICIEMBRE


def formatear_total_matricula(total):
    return f"Total de matricula: {total:.2f}"


def imprimir_total_matricula(total):
    print(formatear_total_matricula(total))


def obtener_mes_actual(reloj=date.today):
    return reloj().month


def main():
    total = calcular_total_matricula(
        costo_base=1000,
        tipo_estudiante=TIPO_NUEVO,
        tiene_beca=True,
        modalidad=MODALIDAD_VIRTUAL,
        mes=obtener_mes_actual(),
    )
    imprimir_total_matricula(total)


if __name__ == "__main__":
    main()
