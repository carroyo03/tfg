import reflex as rx
from tfg_app.styles.styles import color

class AppState(rx.State):
    signed_in: bool = False

    def sign_in(self):
        self.signed_in = True
        return rx.redirect("/")
def sign_in_v1() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.image(
                src="/icons/KPMG_NoCP_White.png",
                width="5em",
                height="auto",
            ),
            rx.heading("Bienvenido a KPMG Predict", _as="h1"),
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
                _hover={"bg": "white.100"},
                on_click=AppState.sign_in,
            ),
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
                _hover={"bg": "gray.100"},
                on_click=AppState.sign_in,
                display="flex",
                justify_content="center"
            ),
            width="100%",
            height="100vh",
            color="white",
            justify="center",
            align="center"
        ),
        width="100%",
        height="100vh",
        display="flex",
        align_items="center",
        justify_content="center",
    )



"""
import reflex as rx
import reflex_chakra as rc
from tfg_app.styles.styles import color
import os
import httpx
import re
import json
from reflex_magic_link_auth import MagicLinkAuthState,send_magic_link_mailgun
import reflex_google_recaptcha_v2
#import pyodbc
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

LOGIN_ROUTE = "/sign-in"
reflex_google_recaptcha_v2.set_site_key(os.getenv("RECAPTCHA_SITE_KEY"))
reflex_google_recaptcha_v2.set_secret_key(os.getenv("RECAPTCHA_SECRET_KEY"))

class SupabaseService:
    def __init__(self):
        self.supabase = create_client(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )

    def get_client(self):
        return self.supabase

class State(rx.State):
    login_error: str = ""
    email: str = ""
    user: dict = {}


    def set_email(self, email: str):
        # Validar el formato del email
        if email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.email = email
        else:
            self.email = ""
            self.login_error = "Por favor, introduce un email válido."
    
    @rx.var(cache=True)
    def is_prod_mode(self)->bool:
        return rx.utils.exec.is_prod_mode()
    @rx.event
    async def handle_submit_login(self):
        magic_link = await self.get_state(MagicLinkAuthState)
        self.login_error = ""
        if not self.email:
            self.login_error = "Por favor, introduce un email"
            return
        
        # Validar el email antes de la consulta
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            self.login_error = "Por favor, introduce un email válido."
            return
        
        try:
            supabase= supabase_service.get_client()
            # Verificar si el email existe en la base de datos
            resp = supabase.table("emails").select("*").eq("user_email", self.email).execute()
            if not resp.get("data"):
                self.login_error = "Email no registrado."
                return

            # Generar OTP para el Magic Link
            record, otp = magic_link._generate_otp(self.email)
            if otp is None:
                self.login_error = (
                    "Demasiados intentos, intenta más tarde."
                    if record else "Error al enviar el correo, intenta más tarde."
                )
                return

            # Validar reCAPTCHA en modo producción
            if self.is_prod_mode:
                recaptcha_state = await self.get_state(
                    reflex_google_recaptcha_v2.GoogleRecaptchaV2State
                )
                if not recaptcha_state.token_is_valid:
                    self.login_error = "Verificación de CAPTCHA fallida. Intenta nuevamente."
                    return

            # Redirigir a la página de confirmación
            yield rx.redirect("/check-your-email")

            # Enviar Magic Link por correo
            if self.is_prod_mode:
                send_magic_link_mailgun(
                    email=self.email,
                    otp=otp,
                    base_url=magic_link._get_magic_link(record, otp),
                    site_name="KPMG Predict"
                )
            else:
                print(f"Magic Link: {magic_link._get_magic_link(record, otp)}")

        except Exception as e:
            self.login_error = f"Error: {str(e)}"
    @rx.event    
    async def handle_redirect(self,token: str):
        try:
            supabase = self.supabase_service.get_client()
            email = await self.validate_magic_link(token)
            resp = supabase.table("emails").select("*").eq("email", email).execute()
            if resp.get("data"):
                self.user = resp.get("data")[0]
                return rx.redirect("/")
            else:
                self.login_error = "Usuario no registrado"
                return rx.redirect("/login")
        except Exception as e:
            self.login_error = f"Error:{str(e)}"
            return rx.redirect("/login")
        
    @rx.event
    async def on_load(self):
        if not self.user:
            return rx.redirect(LOGIN_ROUTE)



def login_page() -> rx.Component:
    return rx.vstack(
        rx.form(
            rx.vstack(
                rx.center(
                    rx.image(
                        src="/icons/KPMG_NoCP_White.png",
                        width="5em",
                        height="auto",
                    ),
                    rx.heading(
                        "Bienvenido a KPMG Predict",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    rx.cond(
                        State.login_error != "",
                        rx.text(
                            State.login_error,
                            color="red",
                            size="2",
                            width="100%",
                        ),
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                rx.vstack(
                    rx.text(
                        "Correo electrónico",
                        size="3",
                        weight="medium",
                        text_align="left",
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Introduce tu email",
                        auto_complete=True,
                        on_change=State.set_email,
                        type="email",
                        size="3",
                        width="100%",
                    ),
                    rx.cond(
                        State.is_prod_mode,
                        reflex_google_recaptcha_v2.google_recaptcha_v2()
                    ),
                    spacing="2",
                    width="100%",
                ),
                rc.button(
                    "Continuar",
                    type="submit",
                    size="md",
                    width="100%",
                    bg=color.CONTENT.value,
                    color="white",
                    _hover={"bg": color.SECONDARY.value},
                ),
                spacing="6",
                width="100%",
                box_shadow="0 .25rem .375rem #0003",
            ),
            id="login-form",
            on_submit=State.handle_submit_login,
            on_mount=MagicLinkAuthState.get_base_url,
            reset_on_submit=True
        ),
        max_width="28em",
        size="4",
        width="100%",
        overflow="hidden",
        color="white",
    )
"""