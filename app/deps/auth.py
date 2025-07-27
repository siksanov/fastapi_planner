import jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Any
from config import settings

context = CryptContext(schemes=['bcrypt'], deprecate='auto')

ALGORITHM = 'HS256'

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {'exp': expire, 'sub': str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)
    return encoded_jwt

def verify_password(password: str, hashed_password: str):
    return context.verify(password, hashed_password)

def password_hash(password: str):
    return context.hash(password)