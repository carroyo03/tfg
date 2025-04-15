import reflex as rx
from tfg_app.views.login.login_form import AppState

def logout_button() -> rx.Component:
    return rx.button(
        "Cerrar sesión",
        on_click=AppState.logout,
        color="white",
        background_color="transparent",
        border="1px solid",
        box_shadow="0 .25rem .375rem #0003",
        width="100%",
        height="auto",
        position="absolute",
        top="1rem",
        right="1rem",
        _hover={"bg":"red", "color":"white"},

    )