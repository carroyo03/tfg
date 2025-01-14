# models.py
import reflex as rx
from datetime import datetime
from typing import Optional

class User(rx.Model, table=True):
    username: str
    email: str
    password_hash: bytes  # Cambiado a bytes para bcrypt
    salt: bytes  # Añadido para bcrypt
    failed_attempts: int = 0
    last_failed_attempt: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = datetime.now()
    last_login: Optional[datetime] = None


