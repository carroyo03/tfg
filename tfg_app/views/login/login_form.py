import reflex as rx
from tfg_app.views.login.state import LoginState, RegisterState


def login_form():
    return rx.vstack(
        rx.heading("Iniciar Sesión"),
        rx.input(
            placeholder="Usuario",
            on_blur=LoginState.set_username,
        ),
        rx.input(
            type_="password",
            placeholder="Contraseña",
            on_blur=LoginState.set_password,
        ),
        rx.button(
            "Iniciar Sesión",
            on_click=LoginState.login,
        ),
        rx.text(LoginState.error),
        rx.link("Registrarse", href="/register"),
        spacing="4",
    )

def register_form():
    return rx.vstack(
        rx.heading("Registro"),
        rx.input(
            placeholder="Usuario",
            on_blur=RegisterState.set_username,
        ),
        rx.input(
            placeholder="Email",
            type_="email",
            on_blur=RegisterState.set_email,
        ),
        rx.input(
            type_="password",
            placeholder="Contraseña",
            on_blur=RegisterState.set_password,
        ),
        rx.button(
            "Registrarse",
            on_click=RegisterState.register,
        ),
        rx.text(RegisterState.error),
        rx.link("Ya tengo cuenta", href="/login"),
        spacing="4",
    )