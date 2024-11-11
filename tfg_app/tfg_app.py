import reflex as rx
from .views.header.header import header
from .components.navbar import navbar
from .styles import styles
from .styles.fonts import Font

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

app = rx.App(style=styles.BASE_STYLE, stylesheets=[f"https://fonts.googleapis.com/css?family={font.value}" for font in Font])
app.add_page(index)
