import jwt
import secrets
from jwt.exceptions import JWTException
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Any, Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from models.user import User
from sqlmodel import Session, SQLModel
from pydantic import ValidationError
from db import get_user_by_email


class TokenPayload(SQLModel):
    sub: str | None = None


reusable_oauth2 = OAuth2PasswordBearer(
    'api/v1/login/token'
)

context = CryptContext(schemes=['bcrypt'], deprecate='auto')

ALGORITHM = 'HS256'

TokenGet = Annotated[str, Depends(reusable_oauth2)]

secret = secrets.token_urlsafe(32)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {'exp': expire, 'sub': str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret, ALGORITHM)
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


def auth_user(session: Session, token: TokenGet):
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except HTTPException(JWTException, ValidationError):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            'Не удалось проверить учетные данные'
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            'Пользователь не найден'
        )
    if not user.is_active:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Пользователь неактивен'
        )
    return user


AuthUser = Annotated[User, Depends(auth_user)]
