import jwt
import secrets
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Any, Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from models.user import User
from sqlmodel import Session
from db import get_user_by_email

reusable_oauth2 = OAuth2PasswordBearer(
    'api/v1/login/token'
)

context = CryptContext(schemes=['bcrypt'], deprecate='auto')

ALGORITHM = 'HS256'

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {'exp': expire, 'sub': str(subject)}
    encoded_jwt = jwt.encode(to_encode, secrets.token_urlsafe(32), 'HS256')
    return encoded_jwt


def verify_password(password: str, hashed_password: str):
    return context.verify(password, hashed_password)


def password_hash(password: str):
    return context.hash(password)


def authenticate(session: Session, email: str, password: str) -> User:
    db_user = get_user_by_email(session, email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
