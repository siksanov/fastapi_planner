import uuid
from collections.abc import Generator

from sqlmodel import create_engine, SQLModel, Session, select
from fastapi import Depends
from typing import Annotated
from auth import password_hash
from models.user import User, UserCreate, UserUpdate
from models.item import Item, ItemCreate


engine = create_engine(
    'postgresql+psycopg//localhost:5432@postgres:postgres',
    echo=True,)
SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionGet = Annotated[Session, Depends(get_db)]


def create_user(session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={
            'hashed_password': password_hash(user_create.password)
        }
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(session: Session, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if 'password' in user_data:
        password = user_data['password']
        extra_data['hashed_password'] = password_hash(password)
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(session: Session, email: str) -> User | None:
    query = select(User).where(User.email == email)
    db_user = session.exec(query)
    return db_user


def create_item(session: Session,
                item_create: ItemCreate,
                owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_create, update={'owner_id': owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
