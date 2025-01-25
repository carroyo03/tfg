import reflex as rx
from tfg_app.views.pilar1.pilar1form import header
from tfg_app.components.navbar import navbar
from tfg_app.styles import styles,colors
from tfg_app.styles.fonts import Font
from tfg_app.backend.main import calcular_pension
from tfg_app.views.results.result import final_result
from tfg_app.views.pilar1.pilar1results import results_pilar1
from tfg_app.styles.styles import Size as size
from typing import Callable
from datetime import datetime
import os
from reflex_clerk import ClerkState
import reflex_clerk as clerk
from dotenv import load_dotenv
from tfg_app.views.login.login_form import AppState,sign_in_v1
#from tfg_app.views.login.clerk_components import sign_in_page
#from tfg_app.views.login.login_form import login_page,LOGIN_ROUTE,State as AuthState
"""
@rx.page("/sign-in")
def login():
    return lform()


load_dotenv()






@rx.page(LOGIN_ROUTE)
def sign_in():
    return rx.flex(
        login_page(),
        width="100%",
        height="100vh",
        align_items="center",
        justify_content="center",
    )


@rx.page("/check-your-email")
def check_email():
    return rx.box(
        rx.heading("Check your email inbox or spam folder", size="3"),
    )
"""




@rx.page("/sign-in")
def sign_in():
    return sign_in_v1()


@rx.page("/")
def index():
    return rx.cond(
        AppState.signed_in,
        rx.box(
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
        ),
        sign_in_v1()
    )


@rx.page("/pilar1")#,on_load=AuthState.on_load)
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
        rx.center(
            rx.button(
                "Atrás", 
                on_click=rx.redirect("/"), 
                color="white",
                background_color="transparent",
                border="1px solid",
                box_shadow="0 .25rem .375rem #0003",
                width="20%",
                height="auto"
            ),
            rx.button(
                "Siguiente",
                on_click=rx.redirect("/result"),
                background_color="white",
                color=colors.Color.BACKGROUND.value,
                border="1px solid",
                box_shadow="0 .25rem .375rem #0003",
                width="20%",
                height="auto"
            ),
            width="100%",
            margin_top="-7rem",
            spacing="2",
            align="center",
            justify="center",
        ),

        width="100%",
        min_height="100vh",
        spacing="0",
        align_items="stretch",
        background_color="#00338D",  # Fondo azul
    )

@rx.page("/result")#,on_load=AuthState.on_load) 
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


app = rx.App(style=styles.BASE_STYLE, stylesheets=[f"https://fonts.googleapis.com/css?family={font.value}" for font in Font if font != Font.TITLE.value])
app.add_page(sign_in)
#app.add_page(check_email)
app.add_page(index)
app.api.add_api_route("/calcular_pension/", calcular_pension, methods=["POST"])
app.add_page(pilar1)

