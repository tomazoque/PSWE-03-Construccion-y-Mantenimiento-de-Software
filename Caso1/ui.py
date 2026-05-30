from __future__ import annotations

import logging
import smtplib
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from database import DATABASE_ERRORS
from models import User
from services import AuthService
from validators import (
    token_valido,
    validar_email_recuperacion,
    validar_login_form,
    validar_nueva_clave,
)


class App(tk.Tk):
    def __init__(self, auth_service: AuthService):
        super().__init__()

        self.auth_service = auth_service
        self.title("Sistema Demo - Login 2FA")
        self.geometry("500x350")
        self.resizable(False, False)

        self.current_user: Optional[User] = None
        self.show_login()

    def clear_screen(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def show_error(self, message: str) -> None:
        self.clear_screen()

        tk.Label(self, text="Pantalla de error", font=("Arial", 18, "bold")).pack(pady=25)
        tk.Label(self, text=message, fg="red", wraplength=420).pack(pady=10)
        tk.Button(self, text="Volver al login", command=self.show_login, width=20).pack(pady=20)

    def add_title(self, text: str) -> None:
        tk.Label(self, text=text, font=("Arial", 18, "bold")).pack(pady=20)

    def run_action(self, action: Callable[[], None]) -> None:
        try:
            action()
        except DATABASE_ERRORS:
            logging.exception("Error de base de datos")
            self.show_error("No fue posible completar la operacion en la base de datos.")
        except smtplib.SMTPException:
            logging.exception("Error enviando correo")
            self.show_error("No fue posible enviar el correo. Revise la configuracion SMTP.")
        except Exception:
            logging.exception("Error no controlado")
            self.show_error("Ocurrio un error inesperado. Intente nuevamente.")

    def show_login(self) -> None:
        self.clear_screen()
        self.current_user = None

        self.add_title("Inicio de sesion")

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_email = tk.Entry(frame, width=35)
        entry_email.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Clave:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entry_password = tk.Entry(frame, width=35, show="*")
        entry_password.grid(row=1, column=1, pady=5)

        def login() -> None:
            email = entry_email.get().strip()
            password = entry_password.get().strip()

            is_valid, message = validar_login_form(email, password)
            if not is_valid:
                self.show_error(message)
                return

            user = self.auth_service.authenticate(email, password)
            if user is None:
                self.show_error("Usuario o clave incorrectos.")
                return

            self.auth_service.send_login_token(user)
            self.current_user = user
            self.show_2fa()

        tk.Button(self, text="Ingresar", command=lambda: self.run_action(login), width=20).pack(pady=10)
        tk.Button(self, text="Recuperar clave", command=self.show_password_recovery, width=20).pack()

    def show_2fa(self) -> None:
        self.clear_screen()

        self.add_title("Doble autenticacion")
        tk.Label(self, text="Digite el token enviado por email.").pack(pady=5)

        entry_token = tk.Entry(self, width=20)
        entry_token.pack(pady=10)

        def verify() -> None:
            token = entry_token.get().strip()

            if not token:
                self.show_error("Debe digitar el token.")
                return
            if not token_valido(token):
                self.show_error("El token debe tener 6 digitos.")
                return
            if self.current_user is None:
                self.show_error("La sesion expiro. Inicie sesion nuevamente.")
                return

            if self.auth_service.verify_login_token(self.current_user, token):
                self.show_menu()
            else:
                self.show_error("Token invalido, expirado o ya utilizado.")

        tk.Button(self, text="Verificar token", command=lambda: self.run_action(verify), width=20).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.show_login, width=20).pack()

    def show_password_recovery(self) -> None:
        self.clear_screen()

        self.add_title("Recuperacion de clave")
        tk.Label(self, text="Digite su email registrado.").pack(pady=5)

        entry_email = tk.Entry(self, width=35)
        entry_email.pack(pady=10)

        def send_recovery_token() -> None:
            email = entry_email.get().strip()

            is_valid, message = validar_email_recuperacion(email)
            if not is_valid:
                self.show_error(message)
                return

            user_id = self.auth_service.request_password_recovery(email)
            if user_id is None:
                self.show_error("No existe un usuario con ese email.")
                return

            self.show_change_password(user_id)

        tk.Button(self, text="Enviar token", command=lambda: self.run_action(send_recovery_token), width=20).pack(pady=10)
        tk.Button(self, text="Volver", command=self.show_login, width=20).pack()

    def show_change_password(self, user_id: int) -> None:
        self.clear_screen()

        self.add_title("Cambiar clave")

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_token = tk.Entry(frame, width=30)
        entry_token.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Nueva clave:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entry_password = tk.Entry(frame, width=30, show="*")
        entry_password.grid(row=1, column=1, pady=5)

        def change() -> None:
            token = entry_token.get().strip()
            new_password = entry_password.get().strip()

            is_valid, message = validar_nueva_clave(token, new_password)
            if not is_valid:
                self.show_error(message)
                return

            if not self.auth_service.change_password(user_id, token, new_password):
                self.show_error("Token invalido, expirado o ya utilizado.")
                return

            messagebox.showinfo("Clave actualizada", "La clave fue actualizada correctamente.")
            self.show_login()

        tk.Button(self, text="Cambiar clave", command=lambda: self.run_action(change), width=20).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.show_login, width=20).pack()

    def show_menu(self) -> None:
        self.clear_screen()

        name = self.current_user.nombre if self.current_user else "Usuario"
        self.add_title(f"Menu principal - {name}")

        menu_options = (
            ("Inicio", "Pantalla de inicio"),
            ("Opcion 1", "Funcionalidad en construccion"),
            ("Opcion 2", "Funcionalidad en construccion"),
            ("Opcion 3", "Funcionalidad en construccion"),
        )

        for title, message in menu_options:
            tk.Button(
                self,
                text=title,
                width=25,
                command=lambda t=title, m=message: messagebox.showinfo(t, m),
            ).pack(pady=5)

        tk.Button(self, text="Salir", width=25, command=self.show_login).pack(pady=20)
