"""
Programa didáctico:
Login con MSSQL + recuperación de clave por email + doble autenticación por email.

Curso: Construcción y Mantenimiento de Software

Requisitos:
    pip install pyodbc

Para enviar correos reales:
    Configurar variables de ambiente:
        SMTP_SERVER
        SMTP_PORT
        SMTP_USER
        SMTP_PASSWORD
        SMTP_FROM

Ejemplo en Windows PowerShell:
    setx SMTP_SERVER "smtp.gmail.com"
    setx SMTP_PORT "587"
    setx SMTP_USER "su_correo@gmail.com"
    setx SMTP_PASSWORD "clave_de_aplicacion"
    setx SMTP_FROM "su_correo@gmail.com"

Si no configura SMTP, el programa mostrará el token en consola.
"""

import os
import re
import ssl
import hashlib
import secrets
import smtplib
import tkinter as tk
from tkinter import messagebox
from email.message import EmailMessage
from datetime import datetime, timedelta

import pyodbc


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "CMSoftwareDemo")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Si usa autenticación integrada de Windows:
CONNECTION_STRING = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_NAME};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# Si prefiere usuario SQL Server, comente el CONNECTION_STRING anterior y use esto:
# DB_USER = os.getenv("DB_USER", "sa")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "SuClave")
# CONNECTION_STRING = (
#     f"DRIVER={{{DB_DRIVER}}};"
#     f"SERVER={DB_SERVER};"
#     f"DATABASE={DB_NAME};"
#     f"UID={DB_USER};"
#     f"PWD={DB_PASSWORD};"
#     "TrustServerCertificate=yes;"
# )


# ==========================================================
# VALIDACIONES
# ==========================================================

def email_valido(email):
    patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(patron, email) is not None


def clave_valida(clave):
    """
    Regla didáctica:
    - No vacía
    - Solo letras, números y el caracter especial #
    """
    if not clave:
        return False
    return re.match(r"^[A-Za-z0-9#]+$", clave) is not None


def validar_login_form(email, clave):
    if not email.strip():
        return False, "El email es obligatorio."
    if not clave.strip():
        return False, "La clave es obligatoria."
    if not email_valido(email):
        return False, "El formato del email no es válido."
    if not clave_valida(clave):
        return False, "La clave solo puede contener letras, números y el caracter especial #."
    return True, ""


# ==========================================================
# ACCESO A DATOS
# ==========================================================

def obtener_conexion():
    return pyodbc.connect(CONNECTION_STRING)


def hash_clave(clave, salt):
    return hashlib.sha256(salt + clave.encode("utf-8")).digest()


def buscar_usuario_por_email(email):
    sql = """
    SELECT id_usuario, email, clave_hash, clave_salt, nombre, celular, activo
    FROM dbo.Usuario
    WHERE email = ?
    """
    with obtener_conexion() as cn:
        cursor = cn.cursor()
        cursor.execute(sql, email)
        return cursor.fetchone()


def validar_credenciales(email, clave):
    usuario = buscar_usuario_por_email(email)

    if usuario is None:
        return None

    id_usuario, email_bd, clave_hash_bd, clave_salt, nombre, celular, activo = usuario

    if not activo:
        return None

    clave_hash_calculada = hash_clave(clave, bytes(clave_salt))

    if clave_hash_calculada == bytes(clave_hash_bd):
        return {
            "id_usuario": id_usuario,
            "email": email_bd,
            "nombre": nombre,
            "celular": celular
        }

    return None


def guardar_token(id_usuario, token, tipo, minutos=5):
    sql = """
    INSERT INTO dbo.Token2FA(id_usuario, token, tipo, fecha_expira, usado)
    VALUES (?, ?, ?, DATEADD(MINUTE, ?, SYSDATETIME()), 0)
    """
    with obtener_conexion() as cn:
        cursor = cn.cursor()
        cursor.execute(sql, id_usuario, token, tipo, minutos)
        cn.commit()


def validar_token(id_usuario, token, tipo):
    sql_buscar = """
    SELECT TOP 1 id_token
    FROM dbo.Token2FA
    WHERE id_usuario = ?
      AND token = ?
      AND tipo = ?
      AND usado = 0
      AND fecha_expira >= SYSDATETIME()
    ORDER BY fecha_creacion DESC
    """

    sql_usar = """
    UPDATE dbo.Token2FA
    SET usado = 1
    WHERE id_token = ?
    """

    with obtener_conexion() as cn:
        cursor = cn.cursor()
        cursor.execute(sql_buscar, id_usuario, token, tipo)
        row = cursor.fetchone()

        if row is None:
            return False

        id_token = row[0]
        cursor.execute(sql_usar, id_token)
        cn.commit()
        return True


def actualizar_clave(id_usuario, nueva_clave):
    nuevo_salt = secrets.token_bytes(16)
    nuevo_hash = hash_clave(nueva_clave, nuevo_salt)

    sql = """
    UPDATE dbo.Usuario
    SET clave_hash = ?, clave_salt = ?
    WHERE id_usuario = ?
    """

    with obtener_conexion() as cn:
        cursor = cn.cursor()
        cursor.execute(sql, nuevo_hash, nuevo_salt, id_usuario)
        cn.commit()


# ==========================================================
# EMAIL
# ==========================================================

def generar_token():
    return str(secrets.randbelow(900000) + 100000)


def enviar_email(destinatario, asunto, cuerpo):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_server or not smtp_user or not smtp_password:
        print("\n=== MODO DEMO: EMAIL NO CONFIGURADO ===")
        print(f"Para: {destinatario}")
        print(f"Asunto: {asunto}")
        print(cuerpo)
        print("======================================\n")
        return

    mensaje = EmailMessage()
    mensaje["From"] = smtp_from
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)

    contexto = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=contexto)
        server.login(smtp_user, smtp_password)
        server.send_message(mensaje)


# ==========================================================
# INTERFAZ TKINTER
# ==========================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Demo - Login 2FA")
        self.geometry("500x350")
        self.resizable(False, False)

        self.usuario_actual = None

        self.mostrar_login()

    def limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_error(self, mensaje):
        self.limpiar()

        tk.Label(self, text="Pantalla de error", font=("Arial", 18, "bold")).pack(pady=25)
        tk.Label(self, text=mensaje, fg="red", wraplength=420).pack(pady=10)

        tk.Button(self, text="Volver al login", command=self.mostrar_login, width=20).pack(pady=20)

    def mostrar_login(self):
        self.limpiar()

        tk.Label(self, text="Inicio de sesión", font=("Arial", 18, "bold")).pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_email = tk.Entry(frame, width=35)
        entry_email.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Clave:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entry_clave = tk.Entry(frame, width=35, show="*")
        entry_clave.grid(row=1, column=1, pady=5)

        def login():
            email = entry_email.get().strip()
            clave = entry_clave.get().strip()

            valido, mensaje = validar_login_form(email, clave)
            if not valido:
                self.mostrar_error(mensaje)
                return

            try:
                usuario = validar_credenciales(email, clave)
            except Exception as ex:
                self.mostrar_error(f"Error conectando con la base de datos: {ex}")
                return

            if usuario is None:
                self.mostrar_error("Usuario o clave incorrectos.")
                return

            token = generar_token()
            guardar_token(usuario["id_usuario"], token, "LOGIN_2FA", minutos=5)

            enviar_email(
                usuario["email"],
                "Token de doble autenticación",
                f"Hola {usuario['nombre']}, su token de acceso es: {token}. Expira en 5 minutos."
            )

            self.usuario_actual = usuario
            self.mostrar_2fa()

        tk.Button(self, text="Ingresar", command=login, width=20).pack(pady=10)
        tk.Button(self, text="Recuperar clave", command=self.mostrar_recuperar_clave, width=20).pack()

    def mostrar_2fa(self):
        self.limpiar()

        tk.Label(self, text="Doble autenticación", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self, text="Digite el token enviado por email.").pack(pady=5)

        entry_token = tk.Entry(self, width=20)
        entry_token.pack(pady=10)

        def verificar():
            token = entry_token.get().strip()

            if not token:
                self.mostrar_error("Debe digitar el token.")
                return

            if validar_token(self.usuario_actual["id_usuario"], token, "LOGIN_2FA"):
                self.mostrar_menu()
            else:
                self.mostrar_error("Token inválido, expirado o ya utilizado.")

        tk.Button(self, text="Verificar token", command=verificar, width=20).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.mostrar_login, width=20).pack()

    def mostrar_recuperar_clave(self):
        self.limpiar()

        tk.Label(self, text="Recuperación de clave", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self, text="Digite su email registrado.").pack(pady=5)

        entry_email = tk.Entry(self, width=35)
        entry_email.pack(pady=10)

        def enviar_token_recuperacion():
            email = entry_email.get().strip()

            if not email:
                self.mostrar_error("El email es obligatorio.")
                return

            if not email_valido(email):
                self.mostrar_error("El formato del email no es válido.")
                return

            usuario = buscar_usuario_por_email(email)

            if usuario is None:
                self.mostrar_error("No existe un usuario con ese email.")
                return

            id_usuario = usuario[0]
            nombre = usuario[4]

            token = generar_token()
            guardar_token(id_usuario, token, "RECUPERACION", minutos=5)

            enviar_email(
                email,
                "Token de recuperación de clave",
                f"Hola {nombre}, su token de recuperación es: {token}. Expira en 5 minutos."
            )

            self.mostrar_cambiar_clave(id_usuario)

        tk.Button(self, text="Enviar token", command=enviar_token_recuperacion, width=20).pack(pady=10)
        tk.Button(self, text="Volver", command=self.mostrar_login, width=20).pack()

    def mostrar_cambiar_clave(self, id_usuario):
        self.limpiar()

        tk.Label(self, text="Cambiar clave", font=("Arial", 18, "bold")).pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_token = tk.Entry(frame, width=30)
        entry_token.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Nueva clave:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entry_clave = tk.Entry(frame, width=30, show="*")
        entry_clave.grid(row=1, column=1, pady=5)

        def cambiar():
            token = entry_token.get().strip()
            nueva_clave = entry_clave.get().strip()

            if not token:
                self.mostrar_error("Debe digitar el token.")
                return

            if not nueva_clave:
                self.mostrar_error("Debe digitar la nueva clave.")
                return

            if not clave_valida(nueva_clave):
                self.mostrar_error("La clave solo puede contener letras, números y el caracter especial #.")
                return

            if not validar_token(id_usuario, token, "RECUPERACION"):
                self.mostrar_error("Token inválido, expirado o ya utilizado.")
                return

            actualizar_clave(id_usuario, nueva_clave)
            messagebox.showinfo("Clave actualizada", "La clave fue actualizada correctamente.")
            self.mostrar_login()

        tk.Button(self, text="Cambiar clave", command=cambiar, width=20).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.mostrar_login, width=20).pack()

    def mostrar_menu(self):
        self.limpiar()

        nombre = self.usuario_actual["nombre"] if self.usuario_actual else "Usuario"

        tk.Label(self, text=f"Menú principal - {nombre}", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(self, text="Inicio", width=25, command=lambda: messagebox.showinfo("Inicio", "Pantalla de inicio")).pack(pady=5)
        tk.Button(self, text="Opción 1", width=25, command=lambda: messagebox.showinfo("Opción 1", "Funcionalidad en construcción")).pack(pady=5)
        tk.Button(self, text="Opción 2", width=25, command=lambda: messagebox.showinfo("Opción 2", "Funcionalidad en construcción")).pack(pady=5)
        tk.Button(self, text="Opción 3", width=25, command=lambda: messagebox.showinfo("Opción 3", "Funcionalidad en construcción")).pack(pady=5)
        tk.Button(self, text="Salir", width=25, command=self.mostrar_login).pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()
