from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import items, users


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def home():
    return {'message': 'Hello, World!!!'}

app.include_router(items.router, prefix='/api/v1')
app.include_router(users.router, prefix='/api/v1')
