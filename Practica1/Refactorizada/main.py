from calculadora_pago import CalculadoraMatricula
from estudiante import Estudiante


def main():
    estudiante = Estudiante(
        nombre="Ana Rodriguez",
        tipo="nuevo",
        monto=1000,
        modalidad="virtual",
        tiene_beca=True,
    )

    calculadora = CalculadoraMatricula()
    total = calculadora.calcular(estudiante, mes=12)

    print(f"Nombre del estudiante: {estudiante.nombre}")
    print(f"Total a pagar: {total:.2f}")


if __name__ == "__main__":
    main()
