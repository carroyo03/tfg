from typing import Optional
import reflex as rx
from tfg_app.styles.styles import color
import os
from jose import jwk, jwt as jose_jwt
from authlib.integrations.httpx_client import AsyncOAuth2Client
import requests
import jwt
from dotenv import load_dotenv
load_dotenv()




class AppState(rx.State):
    signed_in: bool = False
    guest: bool = False
    user_info: dict = {}
    access_token: str = rx.Cookie(
        name="access_token",
        same_site="strict",
        secure=True,
        max_age=3600,  # 1 hour
    )
    id_token: str = rx.Cookie(
        name="id_token",
        same_site="strict",
        secure=True,
        max_age=3600,  # 1 hour
    )
    refresh_token: str = rx.Cookie(
        name="refresh_token",
        same_site="strict",
        secure=True,
        max_age=3600 * 24 * 30, # 1 month
    )
    oauth_state : str = rx.Cookie(
        name = "oauth_state",
        same_site="strict",
        secure=True,
        max_age=3600, # 1 hour
    )
    error_message: str = ""

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

    COGNITO_VARIABLES = {
        "COGNITO_DOMAIN": COGNITO_DOMAIN,
        "COGNITO_CLIENT_ID": COGNITO_CLIENT_ID,
        "COGNITO_CLIENT_SECRET": COGNITO_CLIENT_SECRET,
        "COGNITO_REDIRECT_URI": COGNITO_REDIRECT_URI,
        "COGNITO_REGION": COGNITO_REGION,
        "COGNITO_USER_POOL_ID": COGNITO_USER_POOL_ID,
        "COGNITO_RESPONSE_TYPE": COGNITO_RESPONSE_TYPE,
        "COGNITO_SCOPE": COGNITO_SCOPE,
        "COGNITO_LOGOUT_URI": COGNITO_LOGOUT_URI,
    }
    for key, value in  COGNITO_VARIABLES.items():
        if value is None:
            raise ValueError(f"Environment variable {key} is not set.")
    
    print("Cognito variables loaded:")
    print(f"{key}: {value}\n" for key, value in COGNITO_VARIABLES.items())

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
        print(f"Generating state: {state}")
        print(f"Redirecting to: {uri}")
        self.oauth_state = state # Store the state in the cookie
        return rx.redirect(uri)
    
    @rx.event
    async def handle_authorize(self):
        code = self.router.page.params.get("code")
        state = self.router.page.params.get("state")
        print(f"Handling authorization with code: {code} and state: {state}")
        if not code or not state:
            print("Missing code or state in /authorize request.")
            self.signed_in = False
            self.guest = False
            return rx.redirect("/sign-in")
        try:
            if self.oauth_state != state:
                print("State mismatch. Possible CSRF attack.")
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

            print(f"Token received: {token}")
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
                issuer=f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}",
                access_token=self.access_token,
            )
            self.user_info = claims
            self.signed_in = True
            self.guest = False
            print("Authentication successful. Redirecting to home page.")
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
            self.error_message = "Error: Session finished... Please sign in again."
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
            return
        if not self.signed_in or not self.access_token or not self.id_token:
            if redirect_url:
                return rx.redirect("/sign-in")
        return
    
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
