import importlib
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await FastAPILimiter.close()

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


app = FastAPI(
    lifespan=lifespan,
    title="hyperchess-api",
    description="Backend for hyperchess website",
)

for router_file in os.listdir("routers"):
    filename = os.fsdecode(router_file)
    if filename.endswith(".py"):
        path = "routers." + filename[:-3]
        router = importlib.import_module(path)
        app.include_router(router.router, prefix="/api")

origins = ["http://localhost:3000"]

app.add_middleware(CORSMiddleware, allow_origins=origins)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
