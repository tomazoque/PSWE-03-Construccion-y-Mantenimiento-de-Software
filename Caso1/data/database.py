from __future__ import annotations

from config import DatabaseConfig

try:
    import pyodbc  # type: ignore[import-not-found]
except ModuleNotFoundError:
    pyodbc = None


class DatabaseDependencyError(RuntimeError):
    pass


DATABASE_ERRORS: tuple[type[BaseException], ...] = (DatabaseDependencyError,)
if pyodbc is not None:
    DATABASE_ERRORS = (DatabaseDependencyError, pyodbc.Error)


def get_connection(db_config: DatabaseConfig):
    if pyodbc is None:
        raise DatabaseDependencyError("Debe instalar pyodbc con: pip install pyodbc")
    return pyodbc.connect(db_config.connection_string)


def obtener_conexion(db_config: DatabaseConfig | None = None):
    return get_connection(db_config or DatabaseConfig())
