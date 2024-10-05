import importlib
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from pydantic2ts import generate_typescript_defs


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create redis connection for ratelimiter
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)

    # Create database tables from ORM models
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield
    await FastAPILimiter.close()


app = FastAPI(
    lifespan=lifespan,
    title="hyperchess-api",
    description="Backend for hyperchess website",
)

# Create typescript types from pydantic models
for router_file in os.listdir("routers"):
    filename = os.fsdecode(router_file)
    if filename.endswith(".py"):
        path = "routers." + filename[:-3]
        generate_typescript_defs(
            path, f"../frontend/src/lib/types/{filename[:-3]}Types.ts"
        )
        router = importlib.import_module(path)
        app.include_router(router.router, prefix="/api")

for util_file in os.listdir("util"):
    filename = os.fsdecode(util_file)
    if filename.endswith(".py"):
        path = "util." + filename[:-3]
        generate_typescript_defs(
            path, f"../frontend/src/lib/types/{filename[:-3]}Types.ts"
        )

origins = ["http://localhost:5173", "http://localhost:4173", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
