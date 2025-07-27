from sqlmodel import create_engine, SQLModel
from models.user import User

engine = create_engine(
    'postgresql+psycopg//localhost:5432@postgres:postgres',
    echo=True,)

SQLModel.metadata.create_all(engine)







