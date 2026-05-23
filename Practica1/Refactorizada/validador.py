from reglas_pago import MODALIDADES_VALIDAS, TIPOS_ESTUDIANTE_VALIDOS


class ValidadorMatricula:
    @staticmethod
    def validar(estudiante):
        if not isinstance(estudiante.nombre, str) or not estudiante.nombre.strip():
            raise ValueError("El nombre no puede estar vacio.")

        if estudiante.tipo not in TIPOS_ESTUDIANTE_VALIDOS:
            raise ValueError("El tipo debe ser 'nuevo' o 'regular'.")

        if estudiante.modalidad not in MODALIDADES_VALIDAS:
            raise ValueError("La modalidad debe ser 'virtual' o 'presencial'.")

        if estudiante.monto < 0:
            raise ValueError("El monto no puede ser negativo.")

        if not isinstance(estudiante.tiene_beca, bool):
            raise ValueError("tiene_beca debe ser booleano.")
