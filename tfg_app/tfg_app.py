import reflex as rx
from tfg_app.views.header.header import header
from tfg_app.components.navbar import navbar
from tfg_app.styles import styles
from tfg_app.styles.fonts import Font
from tfg_app.API.main import calcular_pension
from tfg_app.views.page2.pilar2 import pilar2
from tfg_app.views.result.result import final_result
def index():
    return rx.box(
        navbar(),
        rx.vstack(
            header(),
            width="100%",
            max_width=["100%", "90%", "80%", "70%"],
            height="100vh",
            spacing="1em",
            align_items="center",
            margin_bottom="0"
        )
    )
"""
def page2():
    return rx.box(
        navbar(),
        rx.vstack(
            pilar2(),
            width="100%",
            max_width=["100%", "90%", "80%", "70%"],
            height="100vh",
            spacing="1em",
            align_items="center",
            margin_bottom="0"
        )
    )
"""
def result():
    return rx.box(
        navbar(),
        rx.vstack(
            final_result(),
            width="100%",
            max_width=["100%", "90%", "80%", "70%"],
            height="100vh",
            spacing="1em",
            align_items="center",
            margin_bottom="0"
        )
    )


app = rx.App(style=styles.BASE_STYLE, stylesheets=[f"https://fonts.googleapis.com/css?family={font.value}" for font in Font])
app.add_page(index)
app.api.add_api_route("/calcular_pension/", calcular_pension, methods=["POST"])
app.add_page(result)
