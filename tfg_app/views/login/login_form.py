from typing import Optional
import reflex as rx
from tfg_app.styles.styles import color
import os
from jose import jwk, jwt as jose_jwt
from authlib.integrations.httpx_client import AsyncOAuth2Client
import requests
import jwt
from time import time
from dotenv import load_dotenv
load_dotenv()




class AppState(rx.State):
    signed_in: bool = False
    guest: bool = False
    user_info: dict = {}
    access_token: str = ""
    id_token: str = ""
    refresh_token: str = ""
    oauth_state : str = rx.Cookie(
        name = "oauth_state",
        same_site="strict",
        secure=True,
    )

    # Cognito configuration
    COGNITO_DOMAIN : Optional[str] = os.environ.get("COGNITO_DOMAIN")
    COGNITO_CLIENT_ID : Optional[str] = os.environ.get("COGNITO_CLIENT_ID")
    COGNITO_CLIENT_SECRET : Optional[str] = os.environ.get("COGNITO_CLIENT_SECRET")
    COGNITO_REDIRECT_URI : Optional[str] = os.environ.get("COGNITO_REDIRECT_URI")
    COGNITO_REGION : Optional[str] = os.environ.get("COGNITO_REGION")
    COGNITO_USER_POOL_ID : Optional[str] = os.environ.get("COGNITO_USER_POOL_ID")
    COGNITO_RESPONSE_TYPE : Optional[str] = os.environ.get("COGNITO_RESPONSE_TYPE")
    COGNITO_SCOPE : Optional[str] = os.environ.get("COGNITO_SCOPE")
    COGNITO_LOGOUT_URI : Optional[str] = os.environ.get("COGNITO_LOGOUT_URI")

    @rx.event
    def sign_in(self):
        client = AsyncOAuth2Client(
            client_id=self.COGNITO_CLIENT_ID,
            client_secret=self.COGNITO_CLIENT_SECRET,
            redirect_uri=self.COGNITO_REDIRECT_URI,
            scope=self.COGNITO_SCOPE.replace("+", " "),
        )
        authorization_endpoint = f"{self.COGNITO_DOMAIN}/oauth2/authorize"
        uri, state = client.create_authorization_url(authorization_endpoint)
        self.oauth_state = state
        return rx.redirect(uri)
    
    @rx.event
    async def handle_authorize(self,code:str, state:str):
        try:
            if self.oauth_state != state:
                self.signed_in = False
                return rx.redirect("/sign-in")
            client = AsyncOAuth2Client(
                client_id=self.COGNITO_CLIENT_ID,
                client_secret=self.COGNITO_CLIENT_SECRET,
                redirect_uri=self.COGNITO_REDIRECT_URI
            )

            token_endpoint = f"{self.COGNITO_DOMAIN}/oauth2/token"
            token = await client.fetch_token(
                token_endpoint,
                grant_type="authorization_code",
                code=code,
                redirect_uri=self.COGNITO_REDIRECT_URI
            )
            self.access_token = token.get("access_token","")
            self.id_token = token.get("id_token","")
            self.refresh_token = token.get("refresh_token","")

            jwks_url = f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
            jwks = requests.get(jwks_url).json()
            header = jwt.get_unverified_header(self.id_token)
            key = next(key for key in jwks["keys"] if key["kid"] == header["kid"])
            public_key = jwk.construct(key)
            claims = jose_jwt.decode(
                self.id_token,
                public_key,
                algorithms=["RS256"],
                audience=self.COGNITO_CLIENT_ID,
                issuer=f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}"
            )
            self.user_info = claims
            self.signed_in = True
            self.guest = False
            return rx.redirect("/")
        
        except Exception as e:
            print(f"Authorization error: {e}")
            self.signed_in = False
            self.guest = False
            return rx.redirect("/sign-in")
    
    @rx.event
    async def refresh_access_token(self):
        if not self.refresh_token:
            print("No refresh token available. Redirecting to sign-in.")
            self.signed_in = False
            self.guest = False
            return rx.redirect("/sign-in")
        

        try:
            client = AsyncOAuth2Client(
                client_id=self.COGNITO_CLIENT_ID,
                client_secret=self.COGNITO_CLIENT_SECRET,
            )
            token_endpoint = f"{self.COGNITO_DOMAIN}/oauth2/token"
            token = await client.fetch_token(
                token_endpoint,
                grant_type="refresh_token",
                refresh_token=self.refresh_token,
            )
            self.access_token = token.get("access_token", "")
            self.id_token = token.get("id_token", self.id_token)
            self.refresh_token = token.get("refresh_token", self.refresh_token)
            print("Access token refreshed successfully.")
        except Exception as e:
            print(f"Error refreshing access token: {e}")
            self.signed_in = False
            self.guest = False
            return rx.redirect("/sign-in")
    
    @rx.event
    async def guest_session(self):
        self.guest = True
        self.signed_in = False
        self.user_info = {}
        self.access_token = ""
        self.id_token = ""
        self.refresh_token = ""
        return rx.redirect("/")
    
    @rx.event
    async def logout(self):
        self.signed_in = False
        self.guest = False
        self.user_info = {}
        self.access_token = ""
        self.id_token = ""
        self.refresh_token = ""
        logout_url = (
            f"{self.COGNITO_DOMAIN}/logout?"
            f"client_id={self.COGNITO_CLIENT_ID}&"
            f"logout_uri={self.COGNITO_LOGOUT_URI}"
        )
        return rx.redirect(logout_url)
    
    @rx.event
    async def check_session(self, redirect_url: Optional[str] = None):
        if self.guest:
            return  # Allow guest access
        if not self.signed_in or not self.id_token:
            if redirect_url:
                return rx.redirect("/sign-in")
            return

        try:
            # Decode id_token to check expiration
            claims = jose_jwt.decode(
                self.id_token,
                None,  # Skip signature verification for expiration check
                options={"verify_signature": False, "verify_aud": False, "verify_iss": False}
            )
            from time import time
            if claims.get("exp", 0) < int(time()):
                print("Token expired. Attempting to refresh.")
                await self.refresh_access_token()
                if not self.signed_in:  # Refresh failed
                    if redirect_url:
                        return rx.redirect("/sign-in")
            print("Token is valid")
        except Exception as e:
            print(f"Session check error: {e}")
            self.signed_in = False
            if redirect_url:
                return rx.redirect("/sign-in")
            
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
                "Iniciar sesión con AWS Cognito",
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
