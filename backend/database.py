import os
from typing import Annotated

from dotenv import find_dotenv, load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())

URL_DATABASE = os.getenv("URL_DATABASE")
assert URL_DATABASE, "URL_DATABASE not found in .env"

engine = create_async_engine(URL_DATABASE)

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=True, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    try:
        async with SessionLocal() as db:
            yield db
    finally:
        await db.close()


db_dependency = Annotated[AsyncSession, Depends(get_db)]
