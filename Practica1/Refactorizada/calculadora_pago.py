from reglas_pago import (
    DESCUENTO_BECA,
    DESCUENTO_DICIEMBRE,
    DESCUENTO_NUEVO,
    DESCUENTO_REGULAR,
    DESCUENTO_VIRTUAL,
    RECARGO_PRESENCIAL,
)
from validador import ValidadorMatricula


class CalculadoraMatricula:
    def calcular(self, estudiante, mes):
        ValidadorMatricula.validar(estudiante)
        self._validar_mes(mes)

        total = estudiante.monto

        if estudiante.tipo == "nuevo":
            total -= estudiante.monto * DESCUENTO_NUEVO
        elif estudiante.tipo == "regular":
            total -= estudiante.monto * DESCUENTO_REGULAR

        if estudiante.tiene_beca:
            total -= estudiante.monto * DESCUENTO_BECA

        if estudiante.modalidad == "virtual":
            total -= DESCUENTO_VIRTUAL
        elif estudiante.modalidad == "presencial":
            total += RECARGO_PRESENCIAL

        if mes == 12:
            total -= DESCUENTO_DICIEMBRE

        return max(total, 0)

    def _validar_mes(self, mes):
        if not isinstance(mes, int):
            raise ValueError("El mes debe ser un numero entero.")

        if mes < 1 or mes > 12:
            raise ValueError("El mes debe estar entre 1 y 12.")
