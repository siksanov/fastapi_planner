import uuid
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, func
from typing import Any

from app.models.item import (
    Item,
    ItemsPublic,
    ItemPublic,
    ItemCreate,
    ItemUpdate
)
from app.core.db import SessionGet, create_item
from app.core.auth import AuthUser


router = APIRouter(prefix='/items', tags=['items'])


@router.get('/', response_model=ItemsPublic)
async def read_items(
    session: SessionGet,
    auth_user: AuthUser,
    skip: int = 0,
    limit: int = 100
) -> Any:
    count_statement = select(func.count()).select_from(Item)
    statement = select(Item).offset(skip).limit(limit)
    if not auth_user.is_superuser:
        count_statement = (
            count_statement
            .where(Item.owner_id == auth_user.id)
        )
        statement = (
            statement
            .where(Item.owner_id == auth_user.id)
        )
    count = session.exec(count_statement).one()
    items = session.exec(statement).all()
    return ItemsPublic(data=items, count=count)


@router.get('/{id}', response_model=ItemPublic)
async def read_item(
    session: SessionGet,
    auth_user: AuthUser,
    id: uuid.UUID
) -> Any:
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Элемент не найден')
    if not auth_user.is_superuser and (item.owner_id != auth_user.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Недостаточно прав')
    return item


@router.post('/', response_model=ItemPublic)
async def new_item(
    session: SessionGet,
    auth_user: AuthUser,
    item_create: ItemCreate
) -> Any:
    item = create_item(session, item_create, auth_user.id)
    return item


@router.put('/{id}', response_model=ItemPublic)
async def update_item(
    session: SessionGet,
    auth_user: AuthUser,
    id: uuid.UUID,
    item_update: ItemUpdate
) -> Any:
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Элемент не найден')
    if not auth_user.is_superuser and (item.owner_id != auth_user.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Недостаточно прав')
    item.sqlmodel_update(item_update)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete('/{id}', response_model=dict)
async def delete_item(
    session: SessionGet,
    auth_user: AuthUser,
    id: uuid.UUID
) -> dict:
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Элемент не найден')
    if not auth_user.is_superuser or (item.owner_id != auth_user.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Недостаточно прав')
    session.delete(item)
    session.commit()
    return {'message': f'Элемент {id} удалён'}
