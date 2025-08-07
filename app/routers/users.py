from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, func

from models.user import (
    UsersPublic,
    UserPublic,
    User,
    UserRegister,
    UserCreate
)
from deps.db import (
    SessionGet,
    get_user_by_email,
    create_user
)

router = APIRouter(prefix='/users', tags='users')


@router.get('/', response_model=UsersPublic)
async def read_users(
    session: SessionGet, skip: int = 0, limit: int = 100
) -> UsersPublic:
    count_statement = select(func.conut()).select_from(User)
    count = session.exec(count_statement).one()
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return UsersPublic(count, users)


@router.post('/signup', response_model=UserPublic)
async def register_user(
    session: SessionGet, user_register: UserRegister
) -> User:
    user = get_user_by_email(session, user_register.email)
    if user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Пользователь с таким адресом электронной почты \
                уже существует в системе')
    user_create = UserCreate.validate(user_register)
    user = create_user(session, user_create)
    return user
