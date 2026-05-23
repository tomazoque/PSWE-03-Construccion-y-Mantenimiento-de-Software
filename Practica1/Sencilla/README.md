# Practica 1 - Calculadora de Matricula Sencilla

Esta practica implementa una calculadora sencilla para determinar el total de matricula que debe pagar un estudiante. El objetivo es aplicar reglas de negocio basicas, validar los datos de entrada y mostrar el monto final.

## Que hace

El programa calcula el total de matricula a partir de:

- Costo base de la matricula
- Tipo de estudiante: `nuevo` o `regular`
- Si el estudiante tiene beca
- Modalidad: `virtual` o `presencial`
- Mes en que se realiza el calculo

Las reglas aplicadas son:

- Estudiante nuevo: 5% de descuento
- Estudiante regular: 3% de descuento
- Estudiante con beca: 20% de descuento
- Modalidad virtual: descuento fijo de 25
- Modalidad presencial: recargo fijo de 50
- Mes de diciembre: descuento fijo de 30
- El total final nunca puede ser menor que cero

Ademas, el programa valida que:

- El costo base no sea negativo
- El tipo de estudiante sea valido
- La beca sea un valor booleano
- La modalidad sea valida
- El mes sea un numero entre 1 y 12

## Estructura del proyecto

```text
matricula.py       Codigo principal de la calculadora de matricula
test_matricula.py  Pruebas automatizadas de la logica de matricula
.gitignore         Archivos y carpetas excluidos del repositorio
```

## Requisitos

- Python 3.12 o superior
- pytest, solo si se desean ejecutar las pruebas

## Como ejecutar la practica

Desde la raiz del proyecto, ejecutar:

```powershell
python matricula.py
```

Si se usa el entorno virtual local:

```powershell
.\.venv\Scripts\python.exe matricula.py
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

Con el entorno virtual local:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Ejemplo de salida

```text
Total de matricula: 725.00
```
