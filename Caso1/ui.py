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

# ── Microsoft Fluent Design System palette ───────────────────────────────────
_BG           = "#F3F3F3"
_WHITE        = "#FFFFFF"
_BLUE         = "#0078D4"
_BLUE_DARK    = "#005A9E"
_BLUE_PRESS   = "#004578"
_BLUE_LIGHT   = "#E1EFFA"
_BLUE_HOVER2  = "#C7E0F4"
_TEXT         = "#323130"
_TEXT_HINT    = "#605E5C"
_RED          = "#D13438"
_DIVIDER      = "#EDEBE9"
_BORDER       = "#8A8886"

_FONT_BODY    = ("Segoe UI", 10)
_FONT_LABEL   = ("Segoe UI", 10)
_FONT_TITLE   = ("Segoe UI", 17, "bold")
_FONT_HEADER  = ("Segoe UI", 13, "bold")
_FONT_TOKEN   = ("Segoe UI", 15)


# ── Widget style helpers ─────────────────────────────────────────────────────

def _style_button(btn: tk.Button, primary: bool = True) -> None:
    if primary:
        btn.config(
            bg=_BLUE, fg=_WHITE, activebackground=_BLUE_DARK, activeforeground=_WHITE,
            relief="flat", cursor="hand2", font=_FONT_BODY, bd=0, padx=16, pady=8,
        )
        btn.bind("<Enter>",          lambda _: btn.config(bg=_BLUE_DARK))
        btn.bind("<Leave>",          lambda _: btn.config(bg=_BLUE))
        btn.bind("<ButtonPress-1>",  lambda _: btn.config(bg=_BLUE_PRESS))
        btn.bind("<ButtonRelease-1>", lambda _: btn.config(bg=_BLUE_DARK))
    else:
        btn.config(
            bg=_BG, fg=_BLUE, activebackground=_BLUE_LIGHT, activeforeground=_BLUE_DARK,
            relief="flat", cursor="hand2", font=_FONT_BODY, bd=0, padx=16, pady=8,
        )
        btn.bind("<Enter>",          lambda _: btn.config(bg=_BLUE_LIGHT))
        btn.bind("<Leave>",          lambda _: btn.config(bg=_BG))
        btn.bind("<ButtonPress-1>",  lambda _: btn.config(bg=_BLUE_HOVER2))
        btn.bind("<ButtonRelease-1>", lambda _: btn.config(bg=_BLUE_LIGHT))


def _style_entry(entry: tk.Entry) -> None:
    entry.config(
        bg=_WHITE, fg=_TEXT, insertbackground=_BLUE,
        relief="solid", bd=1, font=_FONT_BODY,
        highlightthickness=2, highlightcolor=_BLUE, highlightbackground=_BORDER,
    )


def _make_label(parent: tk.Widget, text: str, secondary: bool = False, **kw) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=parent.cget("bg"),
        fg=_TEXT_HINT if secondary else _TEXT,
        font=_FONT_LABEL, **kw,
    )


# ── App ──────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self, auth_service: AuthService):
        super().__init__()

        self.auth_service = auth_service
        self.title("Sistema Demo - Login 2FA")
        self.geometry("520x460")
        self.resizable(False, False)
        self.config(bg=_BG)
        self.wm_attributes("-alpha", 0.0)

        self.current_user: Optional[User] = None

        self._build_chrome()

        self.show_login()
        self._fade_in()

    # ── Chrome (persistent header + footer bar) ──────────────────────────────

    def _build_chrome(self) -> None:
        # Blue header bar
        header = tk.Frame(self, bg=_BLUE, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="  Sistema Demo",
            font=_FONT_HEADER, bg=_BLUE, fg=_WHITE, anchor="w",
        ).pack(side="left", padx=18, pady=16)

        # 2-px accent line under header
        tk.Frame(self, bg=_BLUE_DARK, height=2).pack(fill="x")

        # Scrollable content area
        self.content = tk.Frame(self, bg=_BG)
        self.content.pack(fill="both", expand=True, padx=40, pady=4)

        # Footer divider
        tk.Frame(self, bg=_DIVIDER, height=1).pack(fill="x", side="bottom")
        tk.Label(
            self, text="Sistema Demo  \u00b7  Login 2FA",
            font=("Segoe UI", 8), bg=_BG, fg=_TEXT_HINT,
        ).pack(side="bottom", pady=4)

    # ── Animation helpers ────────────────────────────────────────────────────

    def _fade_in(self, alpha: float = 0.0) -> None:
        self.wm_attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(12, self._fade_in, min(1.0, round(alpha + 0.1, 2)))

    def _flash_transition(self) -> None:
        """Quick alpha dip to signal a screen change."""
        self.wm_attributes("-alpha", 0.65)
        self.after(70, lambda: self.wm_attributes("-alpha", 1.0))

    def _shake(self, steps: int = 0, orig_x: int = 0) -> None:
        offsets = [10, -10, 8, -8, 5, -5, 3, -3, 0]
        if steps < len(offsets):
            self.geometry(f"+{orig_x + offsets[steps]}+{self.winfo_y()}")
            self.after(35, self._shake, steps + 1, orig_x)

    def _typewriter(self, label: tk.Label, text: str, idx: int = 0) -> None:
        cursor = "\u258c" if idx < len(text) else ""
        label.config(text=text[:idx] + cursor)
        if idx <= len(text):
            self.after(32, self._typewriter, label, text, idx + 1)

    def _slide_in_widgets(self, widgets: list[tuple[tk.Widget, dict]], delay_ms: int = 60) -> None:
        """Reveal a list of (widget, pack_kwargs) tuples with a stagger delay."""
        for w, _ in widgets:
            w.pack_forget()

        def reveal(i: int) -> None:
            if i < len(widgets):
                w, kwargs = widgets[i]
                w.pack(**kwargs)
                self.after(delay_ms, reveal, i + 1)

        self.after(10, reveal, 0)

    # ── Screen helpers ───────────────────────────────────────────────────────

    def clear_screen(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

    def _divider(self) -> None:
        tk.Frame(self.content, bg=_DIVIDER, height=1).pack(fill="x", pady=6)

    def _make_frame(self) -> tk.Frame:
        return tk.Frame(self.content, bg=_BG)

    def add_title(self, text: str) -> tk.Label:
        lbl = tk.Label(self.content, text="", font=_FONT_TITLE, bg=_BG, fg=_TEXT)
        lbl.pack(pady=(14, 4))
        self._typewriter(lbl, text)
        return lbl

    def show_error(self, message: str) -> None:
        self._flash_transition()
        self.clear_screen()

        orig_x = self.winfo_x()

        # Red accent bar
        tk.Frame(self.content, bg=_RED, height=3).pack(fill="x", pady=(0, 10))

        title = tk.Label(self.content, text="", font=_FONT_TITLE, bg=_BG, fg=_RED)
        title.pack(pady=(8, 4))
        self._typewriter(title, "Error")

        _make_label(self.content, message, secondary=True, wraplength=420).pack(pady=8)

        btn = tk.Button(self.content, text="Volver al login", command=self.show_login, width=22)
        _style_button(btn, primary=True)
        btn.pack(pady=18)

        self.after(80, self._shake, 0, orig_x)

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

    # ── Screens ──────────────────────────────────────────────────────────────

    def show_login(self) -> None:
        self._flash_transition()
        self.clear_screen()
        self.current_user = None

        self.add_title("Inicio de sesion")
        self._divider()

        frame = self._make_frame()
        frame.pack(pady=8)

        _make_label(frame, "Email:").grid(row=0, column=0, sticky="e", padx=8, pady=7)
        entry_email = tk.Entry(frame, width=30)
        _style_entry(entry_email)
        entry_email.grid(row=0, column=1, pady=7)

        _make_label(frame, "Clave:").grid(row=1, column=0, sticky="e", padx=8, pady=7)
        entry_password = tk.Entry(frame, width=30, show="\u2022")
        _style_entry(entry_password)
        entry_password.grid(row=1, column=1, pady=7)

        entry_email.focus_set()

        def login() -> None:
            email = entry_email.get().strip()
            password = entry_password.get().strip()
            is_valid, msg = validar_login_form(email, password)
            if not is_valid:
                self.show_error(msg)
                return
            user = self.auth_service.authenticate(email, password)
            if user is None:
                self.show_error("Usuario o clave incorrectos.")
                return
            self.auth_service.send_login_token(user)
            self.current_user = user
            self.show_2fa()

        entry_password.bind("<Return>", lambda _: self.run_action(login))

        btn_frame = self._make_frame()
        btn_frame.pack(pady=14)

        btn_login = tk.Button(btn_frame, text="Ingresar", command=lambda: self.run_action(login), width=16)
        _style_button(btn_login, primary=True)
        btn_login.pack(side="left", padx=6)

        btn_recovery = tk.Button(btn_frame, text="Recuperar clave", command=self.show_password_recovery, width=16)
        _style_button(btn_recovery, primary=False)
        btn_recovery.pack(side="left", padx=6)

    def show_2fa(self) -> None:
        self._flash_transition()
        self.clear_screen()

        self.add_title("Doble autenticacion")
        self._divider()

        _make_label(self.content, "Se envio un token de 6 digitos a su correo.", secondary=True).pack(pady=6)

        entry_token = tk.Entry(self.content, width=12, justify="center", font=_FONT_TOKEN)
        _style_entry(entry_token)
        entry_token.pack(pady=12, ipady=4)
        entry_token.focus_set()

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

        entry_token.bind("<Return>", lambda _: self.run_action(verify))

        btn_frame = self._make_frame()
        btn_frame.pack(pady=10)

        btn_verify = tk.Button(btn_frame, text="Verificar token", command=lambda: self.run_action(verify), width=16)
        _style_button(btn_verify, primary=True)
        btn_verify.pack(side="left", padx=6)

        btn_cancel = tk.Button(btn_frame, text="Cancelar", command=self.show_login, width=16)
        _style_button(btn_cancel, primary=False)
        btn_cancel.pack(side="left", padx=6)

    def show_password_recovery(self) -> None:
        self._flash_transition()
        self.clear_screen()

        self.add_title("Recuperacion de clave")
        self._divider()

        _make_label(self.content, "Digite su email registrado.", secondary=True).pack(pady=6)

        entry_email = tk.Entry(self.content, width=32)
        _style_entry(entry_email)
        entry_email.pack(pady=10)
        entry_email.focus_set()

        def send_recovery_token() -> None:
            email = entry_email.get().strip()
            is_valid, msg = validar_email_recuperacion(email)
            if not is_valid:
                self.show_error(msg)
                return
            user_id = self.auth_service.request_password_recovery(email)
            if user_id is None:
                self.show_error("No existe un usuario con ese email.")
                return
            self.show_change_password(user_id)

        entry_email.bind("<Return>", lambda _: self.run_action(send_recovery_token))

        btn_frame = self._make_frame()
        btn_frame.pack(pady=14)

        btn_send = tk.Button(btn_frame, text="Enviar token", command=lambda: self.run_action(send_recovery_token), width=16)
        _style_button(btn_send, primary=True)
        btn_send.pack(side="left", padx=6)

        btn_back = tk.Button(btn_frame, text="Volver", command=self.show_login, width=16)
        _style_button(btn_back, primary=False)
        btn_back.pack(side="left", padx=6)

    def show_change_password(self, user_id: int) -> None:
        self._flash_transition()
        self.clear_screen()

        self.add_title("Cambiar clave")
        self._divider()

        frame = self._make_frame()
        frame.pack(pady=8)

        _make_label(frame, "Token:").grid(row=0, column=0, sticky="e", padx=8, pady=7)
        entry_token = tk.Entry(frame, width=28)
        _style_entry(entry_token)
        entry_token.grid(row=0, column=1, pady=7)
        entry_token.focus_set()

        _make_label(frame, "Nueva clave:").grid(row=1, column=0, sticky="e", padx=8, pady=7)
        entry_password = tk.Entry(frame, width=28, show="\u2022")
        _style_entry(entry_password)
        entry_password.grid(row=1, column=1, pady=7)

        def change() -> None:
            token = entry_token.get().strip()
            new_password = entry_password.get().strip()
            is_valid, msg = validar_nueva_clave(token, new_password)
            if not is_valid:
                self.show_error(msg)
                return
            if not self.auth_service.change_password(user_id, token, new_password):
                self.show_error("Token invalido, expirado o ya utilizado.")
                return
            messagebox.showinfo("Clave actualizada", "La clave fue actualizada correctamente.")
            self.show_login()

        entry_password.bind("<Return>", lambda _: self.run_action(change))

        btn_frame = self._make_frame()
        btn_frame.pack(pady=14)

        btn_change = tk.Button(btn_frame, text="Cambiar clave", command=lambda: self.run_action(change), width=16)
        _style_button(btn_change, primary=True)
        btn_change.pack(side="left", padx=6)

        btn_cancel = tk.Button(btn_frame, text="Cancelar", command=self.show_login, width=16)
        _style_button(btn_cancel, primary=False)
        btn_cancel.pack(side="left", padx=6)

    def show_menu(self) -> None:
        self._flash_transition()
        self.clear_screen()

        name = self.current_user.nombre if self.current_user else "Usuario"
        self.add_title(f"Bienvenido, {name}")
        self._divider()

        menu_options = (
            ("Inicio",   "Pantalla de inicio",          True),
            ("Opcion 1", "Funcionalidad en construccion", False),
            ("Opcion 2", "Funcionalidad en construccion", False),
            ("Opcion 3", "Funcionalidad en construccion", False),
        )

        stagger: list[tuple[tk.Widget, dict]] = []

        for title, message, primary in menu_options:
            btn = tk.Button(
                self.content, text=title, width=28,
                command=lambda t=title, m=message: messagebox.showinfo(t, m),
            )
            _style_button(btn, primary=primary)
            stagger.append((btn, {"pady": 4}))

        div = tk.Frame(self.content, bg=_DIVIDER, height=1)
        stagger.append((div, {"fill": "x", "pady": 6}))

        btn_salir = tk.Button(self.content, text="Cerrar sesion", width=28, command=self.show_login)
        _style_button(btn_salir, primary=False)
        stagger.append((btn_salir, {"pady": 4}))

        # Staggered reveal animation
        self._slide_in_widgets(stagger, delay_ms=55)
