# Practica 1 - Calculadora de Matricula

Esta practica implementa una calculadora de pago de matricula para estudiantes. El programa aplica descuentos y recargos segun las caracteristicas del estudiante y valida que los datos ingresados sean correctos antes de calcular el monto final.

## Que hace

La calculadora toma un estudiante con los siguientes datos:

- Nombre
- Tipo de estudiante: `nuevo` o `regular`
- Monto base de matricula
- Modalidad: `virtual` o `presencial`
- Indicador de beca

Con esa informacion calcula el total a pagar aplicando estas reglas:

- Estudiante nuevo: 5% de descuento
- Estudiante regular: 3% de descuento
- Estudiante con beca: 20% de descuento
- Modalidad virtual: descuento fijo de 25
- Modalidad presencial: recargo fijo de 50
- Mes de diciembre: descuento fijo de 30
- El total nunca puede ser menor que cero

Tambien valida datos como nombre vacio, tipo invalido, modalidad invalida, monto negativo y mes fuera del rango de 1 a 12.

## Estructura del proyecto

```text
calculadora_pago.py   Logica principal para calcular el pago de matricula
estudiante.py         Modelo de datos del estudiante
reglas_pago.py        Constantes con descuentos, recargos y valores permitidos
validador.py          Validaciones de los datos del estudiante
main.py               Ejemplo de ejecucion del programa
test_calculadora.py   Pruebas automatizadas con pytest
```

## Requisitos

- Python 3.12 o superior
- pytest para ejecutar las pruebas

## Como ejecutar el programa

Desde la raiz del proyecto, ejecutar:

```powershell
python main.py
```

Si se esta usando el entorno virtual incluido localmente:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Como ejecutar las pruebas

Instalar pytest si no esta instalado:

```powershell
python -m pip install pytest
```

Ejecutar las pruebas:

```powershell
python -m pytest
```

O usando el entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Ejemplo de salida

```text
Nombre del estudiante: Ana Rodriguez
Total a pagar: 695.00
```
