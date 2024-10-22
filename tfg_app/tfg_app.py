import reflex as rx
from .views.header.header import header
from .components.navbar import navbar
from .styles import styles
from.styles.fonts import Font

def index():
    return rx.box(
        navbar(),
        rx.vstack(
            header(),
            #body(),
            #footer()
            align="center"
        )
    )

app = rx.App(style=styles.BASE_STYLE, stylesheets=[f"https://fonts.googleapis.com/css?family={font.value}" for font in Font])
app.add_page(index)