# state.py
import reflex as rx
from datetime import datetime, timedelta
import bcrypt
from typing import Optional
import jwt
import os
from tfg_app.views.login.login_models import User

class AuthState(rx.State):
    """Estado base para autenticación."""
    token: Optional[str] = rx.LocalStorage(None)
    error: str = ""
    
    def hash_password(self, password: str) -> tuple[bytes, bytes]:
        """Genera hash y salt para la contraseña."""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        return password_hash, salt
    
    def verify_password(self, password: str, hashed: bytes) -> bool:
        """Verifica la contraseña."""
        return bcrypt.checkpw(password.encode(), hashed)
    
    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.token and self.verify_token())
    
    def verify_token(self) -> bool:
        if not self.token:
            return False
        try:
            jwt.decode(
                self.token, 
                os.getenv("SECRET_KEY"), 
                algorithms=["HS256"]
            )
            return True
        except:
            return False
            
    def create_token(self, user_id: int) -> str:
        expiration = datetime.utcnow() + timedelta(days=1)
        return jwt.encode(
            {"user_id": user_id, "exp": expiration},
            os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )
    
# pages/auth/login.py
class LoginState(AuthState):
    username: str = ""
    password: str = ""
    
    @rx.event
    async def login(self):
        with rx.session() as session:
            user = session.query(User).filter(
                User.username == self.username
            ).first()
            
            # Verificar intentos fallidos
            if user and user.failed_attempts >= 3:
                if user.last_failed_attempt:
                    time_diff = datetime.now() - user.last_failed_attempt
                    if time_diff < timedelta(minutes=15):
                        self.error = "Cuenta bloqueada temporalmente"
                        return
            
            if user and self.verify_password(
                self.password, 
                user.password_hash
            ):
                # Reset failed attempts
                user.failed_attempts = 0
                user.last_login = datetime.now()
                session.commit()
                
                # Create session
                self.token = self.create_token(user.id)
                return rx.redirect("/dashboard")
            
            # Increment failed attempts
            if user:
                user.failed_attempts += 1
                user.last_failed_attempt = datetime.now()
                session.commit()
            
            self.error = "Credenciales inválidas"

# pages/auth/register.py
class RegisterState(AuthState):
    username: str = ""
    email: str = ""
    password: str = ""
    
    @rx.event
    async def register(self):
        with rx.session() as session:
            # Verificar usuario existente
            existing = session.query(User).filter(
                (User.username == self.username) | 
                (User.email == self.email)
            ).first()
            
            if existing:
                self.error = "Usuario o email ya existe"
                return
                
            # Crear nuevo usuario
            password_hash, salt = self.hash_password(self.password)
            new_user = User(
                username=self.username,
                email=self.email,
                password_hash=password_hash,
                salt=salt
            )
            
            session.add(new_user)
            session.commit()
            
            return rx.redirect("/login")