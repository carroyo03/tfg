from typing import Optional
import reflex as rx
from tfg_app.styles.styles import color





class AppState(rx.State):
    signed_in: bool = False
    guest: bool = False

    @rx.event
    async def sign_in(self):
        self.signed_in = True
        return rx.redirect("/")
    @rx.event
    async def check_sign_in(self, redirect_url: Optional[str] = None):
        # Simulación de verificación (reemplaza con tu lógica real)
        if not self.signed_in and not self.guest:
            # Verifica autenticación (por ejemplo, con un token o cookie)
            self.signed_in = True  # O usa tu lógica real
            self.guest = True if not self.signed_in else False
        if not self.signed_in and not self.guest and redirect_url:
            return rx.redirect("/sign-in")
    
    @rx.event
    async def guest_session(self):
        self.guest = True
        return rx.redirect("/")
def continue_as_guest():

    return rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                "Continuar como invitado",
                type="submit",
                size="3",
                padding=["1em", "1.5em", "2em"],
                width=["100%", "50%", "20%"],  # Responsive widths
                max_width="100%",
                bg=color.BACKGROUND.value,
                border=".0625rem solid", 
                color="white",
                box_shadow="0 .25rem .375rem #0003",
                _hover={"transform":"scale(1.02)"},
                display="flex",
                justify_content="center"
                ),
            ),
            rx.dialog.content(
                rx.dialog.title("¿Estás seguro?", style={"color":"white"}),
                rx.dialog.description("Si continúas como invitado, perderás precisión en las predicciones.",style={"color":"white"}),
                rx.flex(
                    rx.dialog.close(
                        rx.button("Cancelar",
                            bg="white",
                            color="navy",
                            border="1px solid",
                            box_shadow="0 .25rem .375rem #0003",
                            _hover={"transform":"scale(1.02)"},  # Añadir hover consistente
                        ),
                        width="50%",
                    ),
                    rx.dialog.close(
                        rx.button("Continuar",
                            bg="navy",
                            color="white",
                            border="1px solid", 
                            box_shadow="0 .25rem .375rem #0003",
                            _hover={"transform":"scale(1.02)"},  # Añadir hover consistente
                            on_click=AppState.guest_session,
                        ),
                        width="50%",
                    ),
                    width="70%",
                    height="auto",
                    spacing="3",
                    margin_top="1rem",
                    justify="end",
                    align="end"
                ),
                bg="navy"
            ),
            
        )
def sign_in_v1() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Bienvenido", _as="h1"),
            rx.text("¿Quieres saber cómo será tu futura jubilación?"),
            rx.button(
                "Iniciar sesión",
                type="submit",
                size="3",
                width=["100%", "50%", "20%"],  # Responsive widths
                margin_x="1em",
                bg="white",
                color=color.BACKGROUND.value,
                border=".0625rem solid",
                box_shadow="0 .25rem .375rem #0003",
                _hover={"transform":"scale(1.02)"},
                on_click=AppState.sign_in,
            ),
            continue_as_guest(),
            width="100%",
            height="100vh",
            color="white",
            justify="center",
            margin_x = "1rem",
            align="center"
        ),
        width="100%",
        height="100vh",
        display="flex",
        align_items="center",
        justify_content="center",
    )
