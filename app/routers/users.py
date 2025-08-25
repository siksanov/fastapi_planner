import uuid
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, func
from typing import Annotated, Any

from app.models.user import (
    UsersPublic,
    UserPublic,
    User,
    UserRegister,
    UserCreate
)
from app.core.db import (
    SessionGet,
    get_user_by_email,
    create_user,
    authenticate
)
from app.core.auth import AuthUser, create_access_token

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=UsersPublic)
async def read_users(
    session: SessionGet, skip: int = 0, limit: int = 100
) -> Any:
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return UsersPublic(data=users, count=count)


@router.get('/{id}', response_model=UserPublic | User)
async def read_user(
    user_id: uuid.UUID,
    session: SessionGet,
    auth_user: AuthUser
) -> Any:
    if user_id == auth_user.id:
        return auth_user
    user = session.get(User, user_id)
    return UserPublic(**user)


@router.post('/signup', response_model=UserPublic)
async def register_user(
    session: SessionGet, user_register: UserRegister
) -> Any:
    user = get_user_by_email(session, user_register.email)
    print(user)
    if user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Пользователь с таким адресом электронной почты \
уже существует')
    user_create = UserCreate.model_validate(user_register)
    user = create_user(session, user_create)
    return user


@router.post('/signin')
async def login_user(
    session: SessionGet,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    user = authenticate(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Неверный логин или пароль'
        )
    elif not user.is_active:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Пользователь деактивирован'
        )
    access_token_expires = timedelta(minutes=60)
    token = create_access_token(user.id, access_token_expires)
    return {'access_token': token, 'token_type': 'Bearer'}


@router.patch('/{id}')
async def recovery_auth_user():
    pass


@router.delete('/{id}', response_model=dict)
async def delete_user(
    session: SessionGet,
    auth_user: AuthUser,
    id: uuid.UUID
) -> Any:
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            'Пользователь не найден'
        )
    if not auth_user.is_superuser or (user.id != auth_user.id):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Недостаточно прав'
        )
    session.delete(user)
    session.commit()
    return {'message': f'Элемент {id} удалён успешно'}
