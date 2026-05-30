# Login 2FA con Python Tkinter y MSSQL

## Archivos

- `schema.sql`: crea la base de datos, tablas y usuario demo.
- `app.py`: punto de entrada de la aplicacion.
- `config.py`: configuracion por variables de ambiente.
- `database.py`: conexion a SQL Server y errores de base de datos.
- `models.py`: modelos de datos usados por la aplicacion.
- `repositories.py`: acceso a datos y consultas SQL.
- `services.py`: autenticacion, tokens, hash de clave y envio de email.
- `validators.py`: validaciones de email, clave, token y formularios.
- `ui.py`: interfaz grafica Tkinter.
- `guia_revision.md`: guia de revision para estudiantes.

## Usuario demo

- Email: `demo@fvncr.org`
- Clave: `demo`

## Instalacion

```bash
pip install pyodbc
```

Debe tener instalado el driver ODBC de SQL Server.

## Ejecucion

1. Ejecutar `schema.sql` en SQL Server Management Studio.
2. Configurar variables de ambiente si el servidor SQL no es `localhost`.
3. Ejecutar:

```bash
python app.py
```

## Variables de ambiente

```bash
DB_SERVER=localhost
DB_NAME=CMSoftwareDemo
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_USER=usuario_sql_opcional
DB_PASSWORD=clave_sql_opcional
TOKEN_EXPIRATION_MINUTES=5
```

Si no se configuran `DB_USER` y `DB_PASSWORD`, se usa autenticacion integrada de Windows.

## Email

Si no configura SMTP, el token se muestra en consola.

Para correo real, configurar variables de ambiente:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=correo@gmail.com
SMTP_PASSWORD=clave_de_aplicacion
SMTP_FROM=correo@gmail.com
```
