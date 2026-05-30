from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
    id_usuario: int
    email: str
    nombre: str
    celular: Optional[str]
