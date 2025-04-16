import reflex as rx
from tfg_app.views.login.login_form import AppState

from tfg_app.styles.colors import Color as color

def logout_button() -> rx.Component:
    return rx.box(
        rx.tablet_and_desktop(
            rx.button(
                "Cerrar sesión",
                on_click=AppState.logout,
                color="white",
                background_color="transparent",
                border="1px solid",
                box_shadow="0 .25rem .375rem #0003",
                width="15%",
                height="auto",
                position="absolute",
                top="1rem",
                right="1rem",
                _hover={"bg":"red", "color":"white"},
                flex_direction="column",
                justify="flex-end"
            )
        ),
        rx.mobile_only(
            rx.icon(
                "log-out",
                on_click=AppState.logout,
                color=color.BACKGROUND.value,
                background_color="white",
                border="1px solid",
                box_shadow="0 .25rem .375rem #0003",
                width="10%",
                height="auto",
                position="absolute",
                top="1rem",
                right="1rem",
                _hover={"background-color":"red", "color":"white"},
                flex_direction="column",
                justify="flex-end"
            )
        )
    )