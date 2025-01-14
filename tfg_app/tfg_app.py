import reflex as rx
from tfg_app.views.header.header import header
from tfg_app.components.navbar import navbar
from tfg_app.styles import styles
from tfg_app.styles.fonts import Font
from tfg_app.API.main import calcular_pension
from tfg_app.views.results.result import final_result
from tfg_app.views.page2.pilar1 import results_pilar1
from tfg_app.styles.styles import Size as size
from typing import Optional
from datetime import datetime

class User(rx.Model, table=True):
    username: str
    email: str
    password_hash: str
    failed_attempts: int = 0
    last_failed_attempt: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    last_login: Optional[datetime] = None




            
@rx.page("/login")
def login_page():
    return rx.vstack(
        rx.heading("Iniciar sesión", size="2xl"),
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="Usuario", 
                    type="text",
                    on_change=AppState.set_username,
                    value=AppState.username,
                    width="100%"
                ),
                rx.input(
                    placeholder="Contraseña", 
                    type="password",
                    on_change=AppState.set_password,
                    value=AppState.password,
                    width="100%"
                ),
                rx.button("Iniciar sesión", on_click=AppState.login, width="100%"),
            )
        )
    )

@rx.page("/")
def index():
    return rx.box(
        navbar(),
        rx.vstack(
            header(),
            width="100%",
            max_width=["100%", "90%", "80%", "70%"],
            height="100vh",
            spacing="1",
            align_items="center",
            margin_bottom="0"
        )
    )

@rx.page("/pilar1")
def pilar1():
    return rx.vstack(
        navbar(),
        rx.box(
            rx.heading(
                "Plan Público de Pensiones",
                color="white",
                font_family=Font.TITLE.value,
                font_size=size.BIG.value,
                font_weight="bold",
                text_align="center",
                width="100%",
                padding_top="3rem"
            ),
            width="100%",
            position="sticky",
            top="0",
            z_index="1",
            background_color="rgba(0, 51, 141, 0.9)",  # Azul semi-transparente
            backdrop_filter="blur(5px)",
        ),
        rx.box(
            results_pilar1(),
            width="100%",
            max_width="800px",  # Limita el ancho máximo del contenido
            margin="0 auto",  # Centra horizontalmente
            margin_top="-5rem",
            padding_x="1rem",  # Añade un poco de padding horizontal
        ),
        width="100%",
        min_height="100vh",
        spacing="0",
        align_items="stretch",
        background_color="#00338D",  # Fondo azul
    )

@rx.page("/result")
def result():
    return rx.box(
        navbar(),
        rx.vstack(
            final_result(),
            width="100%",
            max_width=["100%", "90%", "80%", "70%"],
            height="100vh",
            spacing="1",
            align_items="center",
            margin_bottom="0"
        )
    )


app = rx.App(style=styles.BASE_STYLE, stylesheets=[f"https://fonts.googleapis.com/css?family={font.value}" for font in Font])
app.add_page(index)
app.api.add_api_route("/calcular_pension/", calcular_pension, methods=["POST"])
app.add_page(pilar1)
