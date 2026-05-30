from __future__ import annotations

import logging
import smtplib
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from data import DATABASE_ERRORS
from logic import (
    AuthService,
    UserService,
    token_valido,
    validar_email_recuperacion,
    validar_login_form,
    validar_nueva_clave,
    validar_registro_usuario,
)
from models import User


class App(tk.Tk):
    WINDOW_WIDTH = 720
    WINDOW_HEIGHT = 680

    COLOR_BG = "#f4f7fb"
    COLOR_CARD = "#ffffff"
    COLOR_PRIMARY = "#173b68"
    COLOR_PRIMARY_HOVER = "#24588f"
    COLOR_SECONDARY = "#eef3f9"
    COLOR_TEXT = "#1f2937"
    COLOR_MUTED = "#5f6f85"
    COLOR_BORDER = "#d8e0ea"
    COLOR_ERROR = "#b42318"
    COLOR_SUCCESS = "#1f7a4d"

    FONT_BASE = ("Segoe UI", 10)
    FONT_TITLE = ("Segoe UI", 20, "bold")
    FONT_SUBTITLE = ("Segoe UI", 10)
    FONT_LABEL = ("Segoe UI", 10, "bold")
    FONT_BUTTON = ("Segoe UI", 10, "bold")

    def __init__(self, auth_service: AuthService, user_service: UserService):
        super().__init__()

        self.auth_service = auth_service
        self.user_service = user_service
        self.current_user: Optional[User] = None

        self.title("SecureAccess")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(False, False)
        self.configure(bg=self.COLOR_BG)

        self._configure_styles()
        self._center_window()
        self.show_login()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.COLOR_BG)
        style.configure("Card.TFrame", background=self.COLOR_CARD, relief="flat")
        style.configure("Header.TFrame", background=self.COLOR_CARD)
        style.configure("Form.TFrame", background=self.COLOR_CARD)

        style.configure(
            "Title.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_PRIMARY,
            font=self.FONT_TITLE,
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_MUTED,
            font=self.FONT_SUBTITLE,
        )
        style.configure(
            "Body.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT,
            font=self.FONT_BASE,
        )
        style.configure(
            "Muted.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Error.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_ERROR,
            font=self.FONT_BASE,
        )
        style.configure(
            "Success.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_SUCCESS,
            font=self.FONT_BASE,
        )
        style.configure(
            "Field.TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT,
            font=self.FONT_LABEL,
        )
        style.configure(
            "TEntry",
            fieldbackground="#ffffff",
            foreground=self.COLOR_TEXT,
            insertcolor=self.COLOR_TEXT,
            bordercolor=self.COLOR_BORDER,
            lightcolor=self.COLOR_BORDER,
            darkcolor=self.COLOR_BORDER,
            padding=(10, 8),
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", self.COLOR_PRIMARY)],
            lightcolor=[("focus", self.COLOR_PRIMARY)],
            darkcolor=[("focus", self.COLOR_PRIMARY)],
        )
        style.configure(
            "Primary.TButton",
            background=self.COLOR_PRIMARY,
            foreground="#ffffff",
            bordercolor=self.COLOR_PRIMARY,
            focusthickness=0,
            font=self.FONT_BUTTON,
            padding=(16, 10),
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.COLOR_PRIMARY_HOVER), ("pressed", self.COLOR_PRIMARY_HOVER)],
            foreground=[("disabled", "#d1d5db")],
        )
        style.configure(
            "Secondary.TButton",
            background=self.COLOR_SECONDARY,
            foreground=self.COLOR_PRIMARY,
            bordercolor=self.COLOR_BORDER,
            focusthickness=0,
            font=self.FONT_BUTTON,
            padding=(16, 10),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#e1eaf5"), ("pressed", "#d5e2f0")],
        )

    def _center_window(self) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.WINDOW_WIDTH) // 2
        y = (screen_height - self.WINDOW_HEIGHT) // 2
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

    def clear_screen(self) -> None:
        self.unbind("<Return>")
        for widget in self.winfo_children():
            widget.destroy()

    def _screen(self, title: str, subtitle: str, card_width: int = 500) -> ttk.Frame:
        self.clear_screen()

        shell = ttk.Frame(self, style="App.TFrame", padding=32)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        card = ttk.Frame(shell, style="Card.TFrame", padding=(34, 30, 34, 30))
        card.grid(row=0, column=0)
        card.columnconfigure(0, weight=1)

        header = ttk.Frame(card, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text=title, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=subtitle, style="Subtitle.TLabel", wraplength=card_width - 70).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(6, 0),
        )

        return card

    def _form(self, parent: ttk.Frame) -> ttk.Frame:
        form = ttk.Frame(parent, style="Form.TFrame")
        form.grid(row=1, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)
        return form

    def _field(
        self,
        parent: ttk.Frame,
        label: str,
        row: int,
        *,
        show: str = "",
        width: int = 38,
        validate_digits: bool = False,
        bottom_padding: int = 14,
    ) -> ttk.Entry:
        ttk.Label(parent, text=label, style="Field.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 6))

        validate = "key" if validate_digits else "none"
        validatecommand = None
        if validate_digits:
            validatecommand = (self.register(lambda value: value.isdigit() or value == ""), "%P")

        entry = ttk.Entry(
            parent,
            width=width,
            show=show,
            validate=validate,
            validatecommand=validatecommand,
        )
        entry.grid(row=row + 1, column=0, sticky="ew", pady=(0, bottom_padding))
        return entry

    def _password_toggle(
        self,
        parent: ttk.Frame,
        entries: list[ttk.Entry],
        row: int,
        *,
        bottom_padding: int = 12,
    ) -> tk.BooleanVar:
        show_password = tk.BooleanVar(value=False)

        def toggle() -> None:
            visible = show_password.get()
            for entry in entries:
                entry.configure(show="" if visible else "*")

        check = ttk.Checkbutton(
            parent,
            text="Mostrar clave",
            variable=show_password,
            command=toggle,
        )
        check.grid(row=row, column=0, sticky="w", pady=(0, bottom_padding))
        return show_password

    def _actions(self, parent: ttk.Frame, row: int) -> ttk.Frame:
        actions = ttk.Frame(parent, style="Form.TFrame")
        actions.grid(row=row, column=0, sticky="ew", pady=(4, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        return actions

    def _message_label(self, parent: ttk.Frame, row: int, style: str = "Error.TLabel") -> tuple[tk.StringVar, ttk.Label]:
        message = tk.StringVar(value="")
        label = ttk.Label(parent, textvariable=message, style=style, wraplength=430, justify="left")
        label.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        return message, label

    def _set_focus(self, entry: ttk.Entry) -> None:
        def focus_if_available() -> None:
            if entry.winfo_exists():
                entry.focus_set()

        self.after(100, focus_if_available)

    def _show_info(self, title: str, message: str) -> None:
        messagebox.showinfo(title, message, parent=self)

    def run_action(self, action: Callable[[], None]) -> None:
        try:
            action()
        except DATABASE_ERRORS:
            logging.exception("Error de base de datos")
            self.show_error("No fue posible completar la operacion. Intente nuevamente mas tarde.")
        except smtplib.SMTPException:
            logging.exception("Error enviando correo")
            self.show_error("No fue posible enviar el correo en este momento. Intente nuevamente mas tarde.")
        except Exception:
            logging.exception("Error no controlado")
            self.show_error("Ocurrio un error inesperado. Intente nuevamente.")

    def show_error(self, message: str, back_action: Callable[[], None] | None = None) -> None:
        card = self._screen(
            "No fue posible completar la operacion",
            "Revise la informacion ingresada o vuelva a intentarlo.",
            card_width=540,
        )
        form = self._form(card)

        ttk.Label(form, text="!", style="Error.TLabel", font=("Segoe UI", 34, "bold")).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )
        ttk.Label(form, text=message, style="Body.TLabel", wraplength=460, justify="left").grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 18),
        )

        actions = self._actions(form, 2)
        ttk.Button(
            actions,
            text="Volver",
            style="Primary.TButton",
            command=back_action or self.show_login,
        ).grid(row=0, column=0, columnspan=2, sticky="ew")

    def show_login(self) -> None:
        self.current_user = None
        card = self._screen("SecureAccess", "Inicio de sesion seguro", card_width=500)
        form = self._form(card)

        entry_email = self._field(form, "Email", 0)
        entry_password = self._field(form, "Clave", 2, show="*")
        self._password_toggle(form, [entry_password], 4)

        message, _label = self._message_label(form, 5)

        def login() -> None:
            message.set("")
            email = entry_email.get().strip()
            password = entry_password.get().strip()
            is_valid, validation_message = validar_login_form(email, password)
            if not is_valid:
                message.set(validation_message)
                return

            user = self.auth_service.authenticate(email, password)
            if user is None:
                self.show_error("Usuario o clave incorrectos.", self.show_login)
                return

            self.auth_service.send_login_token(user)
            self.current_user = user
            self.show_2fa()

        self.bind("<Return>", lambda _event: self.run_action(login))

        actions = self._actions(form, 6)
        ttk.Button(
            actions,
            text="Iniciar sesion",
            style="Primary.TButton",
            command=lambda: self.run_action(login),
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Button(
            actions,
            text="Olvido su clave?",
            style="Secondary.TButton",
            command=self.show_password_recovery,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(
            actions,
            text="Registrarse",
            style="Secondary.TButton",
            command=self.show_register,
        ).grid(row=1, column=1, sticky="ew", padx=(6, 0))

        self._set_focus(entry_email)

    def show_register(self) -> None:
        card = self._screen("Registro de usuario", "Cree una cuenta para utilizar el acceso seguro.", card_width=540)
        form = self._form(card)

        entry_name = self._field(form, "Nombre", 0, bottom_padding=10)
        entry_email = self._field(form, "Email", 2, bottom_padding=10)
        entry_phone = self._field(form, "Celular", 4, bottom_padding=10)
        entry_password = self._field(form, "Clave", 6, show="*", bottom_padding=10)
        entry_confirm = self._field(form, "Confirmar clave", 8, show="*", bottom_padding=8)
        self._password_toggle(form, [entry_password, entry_confirm], 10, bottom_padding=8)
        message, _label = self._message_label(form, 11)

        def register() -> None:
            message.set("")
            nombre = entry_name.get().strip()
            email = entry_email.get().strip()
            celular = entry_phone.get().strip()
            clave = entry_password.get().strip()
            confirmar_clave = entry_confirm.get().strip()

            is_valid, validation_message = validar_registro_usuario(nombre, email, celular, clave, confirmar_clave)
            if not is_valid:
                message.set(validation_message)
                return

            user = self.user_service.register_user(nombre, email, celular, clave)
            if user is None:
                message.set("Ya existe un usuario registrado con ese email.")
                entry_email.focus_set()
                return

            self._show_info("Usuario registrado", "El usuario fue registrado correctamente.")
            self.show_login()

        actions = self._actions(form, 12)
        ttk.Button(
            actions,
            text="Registrar",
            style="Primary.TButton",
            command=lambda: self.run_action(register),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(
            actions,
            text="Cancelar",
            style="Secondary.TButton",
            command=self.show_login,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._set_focus(entry_name)

    def show_2fa(self) -> None:
        card = self._screen(
            "Verificacion en dos pasos",
            "Se envio un codigo al correo registrado. Ingreselo para completar el acceso.",
            card_width=520,
        )
        form = self._form(card)

        entry_token = self._field(form, "Codigo de verificacion", 0, width=18, validate_digits=True)
        message, label = self._message_label(form, 2)

        def verify() -> None:
            message.set("")
            label.configure(style="Error.TLabel")
            token = entry_token.get().strip()
            if not token:
                message.set("Debe digitar el token.")
                return
            if not token_valido(token):
                message.set("El token debe tener 6 digitos.")
                return
            if self.current_user is None:
                self.show_error("La sesion expiro. Inicie sesion nuevamente.", self.show_login)
                return

            if self.auth_service.verify_login_token(self.current_user, token):
                label.configure(style="Success.TLabel")
                message.set("Codigo verificado correctamente.")
                self.after(350, self.show_menu)
            else:
                self.show_error("Token invalido, expirado o ya utilizado.", self.show_2fa)

        actions = self._actions(form, 3)
        ttk.Button(
            actions,
            text="Verificar codigo",
            style="Primary.TButton",
            command=lambda: self.run_action(verify),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(
            actions,
            text="Volver al inicio",
            style="Secondary.TButton",
            command=self.show_login,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._set_focus(entry_token)

    def show_password_recovery(self) -> None:
        card = self._screen(
            "Recuperar contrasena",
            "Ingrese el email registrado. Si corresponde, recibira un codigo para crear una nueva clave.",
            card_width=520,
        )
        form = self._form(card)

        entry_email = self._field(form, "Email", 0)
        message, _label = self._message_label(form, 2)

        def send_recovery_token() -> None:
            message.set("")
            email = entry_email.get().strip()
            is_valid, validation_message = validar_email_recuperacion(email)
            if not is_valid:
                message.set(validation_message)
                return

            user_id = self.auth_service.request_password_recovery(email)
            if user_id is None:
                self.show_error("No fue posible iniciar la recuperacion con el email ingresado.", self.show_password_recovery)
                return

            self.show_change_password(user_id)

        actions = self._actions(form, 3)
        ttk.Button(
            actions,
            text="Enviar codigo de recuperacion",
            style="Primary.TButton",
            command=lambda: self.run_action(send_recovery_token),
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Button(
            actions,
            text="Volver al login",
            style="Secondary.TButton",
            command=self.show_login,
        ).grid(row=1, column=0, columnspan=2, sticky="ew")

        self._set_focus(entry_email)

    def show_change_password(self, user_id: int) -> None:
        card = self._screen(
            "Crear nueva contrasena",
            "Use el codigo recibido y defina una clave con letras, numeros y el caracter #.",
            card_width=540,
        )
        form = self._form(card)

        entry_token = self._field(form, "Token recibido", 0, width=18, validate_digits=True)
        entry_password = self._field(form, "Nueva clave", 2, show="*")
        entry_confirm = self._field(form, "Confirmar nueva clave", 4, show="*")
        self._password_toggle(form, [entry_password, entry_confirm], 6)
        ttk.Label(
            form,
            text="Restriccion: solo letras, numeros y #.",
            style="Muted.TLabel",
        ).grid(row=7, column=0, sticky="w", pady=(0, 10))
        message, _label = self._message_label(form, 8)

        def change() -> None:
            message.set("")
            token = entry_token.get().strip()
            new_password = entry_password.get().strip()
            confirm_password = entry_confirm.get().strip()
            is_valid, validation_message = validar_nueva_clave(token, new_password)
            if not is_valid:
                message.set(validation_message)
                return
            if not confirm_password:
                message.set("Debe confirmar la nueva clave.")
                return
            if new_password != confirm_password:
                message.set("La confirmacion de clave no coincide.")
                return

            if not self.auth_service.change_password(user_id, token, new_password):
                self.show_error("Token invalido, expirado o ya utilizado.", lambda: self.show_change_password(user_id))
                return

            self._show_info("Clave actualizada", "La clave fue actualizada correctamente.")
            self.show_login()

        actions = self._actions(form, 9)
        ttk.Button(
            actions,
            text="Actualizar contrasena",
            style="Primary.TButton",
            command=lambda: self.run_action(change),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(
            actions,
            text="Cancelar",
            style="Secondary.TButton",
            command=self.show_login,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._set_focus(entry_token)

    def show_menu(self) -> None:
        user_name = self.current_user.nombre if self.current_user else "Usuario"
        user_email = self.current_user.email if self.current_user else ""

        card = self._screen(
            "SecureAccess",
            "Acceso confirmado al sistema de autenticacion segura.",
            card_width=560,
        )
        form = self._form(card)

        ttk.Label(form, text=f"Bienvenido, {user_name}", style="Body.TLabel", font=("Segoe UI", 15, "bold")).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        if user_email:
            ttk.Label(form, text=user_email, style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 18))

        panel = ttk.Frame(form, style="Card.TFrame", padding=(16, 14, 16, 14))
        panel.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        panel.columnconfigure(0, weight=1)
        ttk.Label(panel, text="Acceso exitoso", style="Success.TLabel", font=("Segoe UI", 12, "bold")).grid(
            row=0,
            column=0,
            sticky="w",
        )
        ttk.Label(
            panel,
            text="La identidad fue validada mediante credenciales y verificacion en dos pasos.",
            style="Body.TLabel",
            wraplength=450,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0))

        menu_options = (
            ("Inicio", "Pantalla de inicio"),
            ("Opcion 1", "Funcionalidad en construccion"),
            ("Opcion 2", "Funcionalidad en construccion"),
            ("Opcion 3", "Funcionalidad en construccion"),
        )

        options = ttk.Frame(form, style="Form.TFrame")
        options.grid(row=3, column=0, sticky="ew", pady=(0, 18))
        options.columnconfigure(0, weight=1)
        options.columnconfigure(1, weight=1)

        for index, (title, message) in enumerate(menu_options):
            ttk.Button(
                options,
                text=title,
                style="Secondary.TButton",
                command=lambda t=title, m=message: messagebox.showinfo(t, m, parent=self),
            ).grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=(0, 6) if index % 2 == 0 else (6, 0),
                pady=(0, 10),
            )

        ttk.Button(
            form,
            text="Cerrar sesion",
            style="Primary.TButton",
            command=self.show_login,
        ).grid(row=4, column=0, sticky="ew")
