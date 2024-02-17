from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

URL_DATABASE = "sqlite+aiosqlite:///./hyperchess.db"

engine = create_async_engine(URL_DATABASE, connect_args={"check_same_thread": False})

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
