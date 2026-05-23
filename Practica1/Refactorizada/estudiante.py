from dataclasses import dataclass


@dataclass
class Estudiante:
    nombre: str
    tipo: str
    monto: float
    modalidad: str
    tiene_beca: bool
