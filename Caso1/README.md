# Login 2FA con Python Tkinter y MSSQL

## Estructura

- `app.py`: punto de entrada de la aplicación.
- `schema.sql`: crea la base de datos, tablas y usuario demo.
- `config/`: configuración por variables de ambiente.
- `data/`: conexión SQL Server y repositorios.
- `logic/`: reglas de negocio, autenticación, registro y validaciones.
- `models/`: modelos de datos.
- `services/`: servicios externos, como correo.
- `ui/`: interfaz gráfica Tkinter.
- `guia_revision.md`: guía de revisión para estudiantes.

## Funcionalidades

- Login contra SQL Server.
- Doble autenticación por token enviado por email o mostrado en consola.
- Recuperación y cambio de clave.
- Registro de nuevos usuarios.
- Validación de celular con formato `####-####`, por ejemplo `8888-8888`.
- Auditoría de login, 2FA, recuperación, cambio de clave y registro.
- Claves guardadas con hash + salt.

## Usuario demo

- Email: `demo@fvncr.org`
- Clave: `demo`

## Instalación

```bash
pip install pyodbc
```

Debe tener instalado el driver ODBC de SQL Server.

## Ejecución

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

Si no se configuran `DB_USER` y `DB_PASSWORD`, se usa autenticación integrada de Windows.

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

## Auditoría

Los eventos se guardan en `dbo.AuditoriaLogin`.

Eventos registrados:

- `LOGIN`
- `LOGIN_2FA`
- `RECUPERACION_CLAVE`
- `CAMBIO_CLAVE`
- `REGISTRO_USUARIO`


## Linter y Type Checking
```
pip install mypy ruff
ruff check .
mypy .
```

## SonarQube

``
pip install pysonar
pysonar \          
  --sonar-host-url=http://localhost:9000 \
  --sonar-token=$SONAR_API_KEY \
  --sonar-project-key=Caso-1
``
