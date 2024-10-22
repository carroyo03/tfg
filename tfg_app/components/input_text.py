import reflex as rx
from tfg_app.styles.fonts import Font
def input_text(title:str,text:str)-> rx.Component:
    return rx.vstack(
        rx.text(
            title,
            color="white"),
        rx.input(
            placeholder=text,
        ),
        font_family=Font.DEFAULT.value
    )