import uuid
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, func
from models.item import Item, ItemsPublic, ItemPublic, ItemCreate
from deps.db import SessionGet, create_item
from deps.auth import AuthUser


router = APIRouter(prefix='/items', tags=['items'])


@router.get('/', response_model=ItemsPublic)
async def read_items(
    session: SessionGet,
    auth_user: AuthUser,
    skip: int = 0,
    limit: int = 100
) -> ItemsPublic:
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
    statement = session.exec(statement).all()
    return ItemsPublic(count, statement)


@router.get('/{id}', response_model=ItemPublic)
async def read_item(
    session: SessionGet,
    auth_user: AuthUser,
    id: uuid.UUID
) -> ItemPublic:
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Элемент не найден')
    if not auth_user.is_superuser and (item.owner_id != auth_user.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Недостаточно прав')


@router.post('/', dependencies=AuthUser, response_model=ItemPublic)
async def new_item(
    session: SessionGet,
    auth_user: AuthUser,
    item_create: ItemCreate
) -> ItemPublic:
    item = create_item(session, item_create, auth_user.id)
    return item

