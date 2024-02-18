import io
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Annotated, Literal

from database import db_dependency
from dotenv import find_dotenv, load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Response, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from jose import ExpiredSignatureError, JWTError, jwt
from jose.constants import ALGORITHMS
from models import Users
from passlib.context import CryptContext
from PIL import Image
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.websockets import WebSocket

load_dotenv(find_dotenv())

# https://github.com/pyca/bcrypt/issues/684
logging.getLogger("passlib").setLevel(logging.ERROR)

router = APIRouter(prefix="/user", tags=["user"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

assert SECRET_KEY, "JWT_SECRET_KEY not found in .env"
assert ALGORITHM, "JWT_ALGORITHM not found in .env"
assert ALGORITHM in ALGORITHMS.SUPPORTED, f"Algorithm {ALGORITHM} not supported"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="user/token")

with open("countries.csv") as f:
    valid_country_codes = {int(line.strip().split(",")[0][-3:]) for line in f}

with open("default_pfp.png", "rb") as f:
    default_pfp = f.read()


class SignupForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(),
        email: EmailStr = Form(),
        password: str = Form(),
    ):
        super().__init__(
            grant_type=None,
            username=username,
            password=password,
            scope="",
            client_id=None,
            client_secret=None,
        )

        self.email = email


class DeleteForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
    ):
        super().__init__(
            grant_type=None,
            username=username,
            password=password,
            scope="",
            client_id=None,
            client_secret=None,
        )


class Token(BaseModel):
    access_token: str
    token_type: str


class EditUserRequest(BaseModel):
    about_me: str | None
    country: int | None


class PublicUserResponse(BaseModel):
    username: str
    about_me: str | None
    country: int | None
    rating: int | None
    registration_date: datetime


class PersonalUserResponse(PublicUserResponse):
    email: str


invalid_auth = HTTPException(
    status_code=401,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_user(user_id: int, db: db_dependency) -> Users:
    statement = select(Users).where(Users.id == user_id)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise invalid_auth

    if user.disabled:
        raise HTTPException(403, detail="Account disabled")

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency
) -> Users:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise invalid_auth

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise invalid_auth

    return await get_user(user_id, db)


user_dependency = Annotated[Users, Depends(get_current_user)]


async def authenticate_user(
    username: str, password: str, db: AsyncSession
) -> Users | Literal[False]:
    statement = select(Users).where(Users.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(user_id: int, expires_delta: timedelta) -> str:
    encode = {
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def user_identifer(request: Request | WebSocket) -> str:
    token = request.headers.get("Authorization")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is not None:
            return user_id
    except:
        pass

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host + ":" + request.scope["path"]


@router.post(
    "/", status_code=201, dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def create_user(
    form_data: Annotated[SignupForm, Depends()],
    db: db_dependency,
) -> None:

    if not all(c.isalnum() for c in form_data.username):
        raise HTTPException(
            400, detail="Username should only contain alphanumeric characters"
        )

    if len(form_data.password) < 6:
        raise HTTPException(400, detail="Password should be at least 6 characters long")

    create_user_model = Users(
        id=random.randrange(0, 9223372036854775807),
        username=form_data.username,
        email=form_data.email,
        password=bcrypt_context.hash(form_data.password),
        registration_date=datetime.now(),
    )

    db.add(create_user_model)
    try:
        await db.commit()
    except:
        raise HTTPException(500, detail="Failed to add user to database")


@router.post(
    "/token",
    response_model=Token,
    dependencies=[Depends(RateLimiter(times=3, seconds=10))],
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
) -> dict[str, str]:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(401, detail="Could not validate user")

    token = create_access_token(user.id, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}


@router.delete(
    "/", status_code=200, dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def delete_user(
    form_data: Annotated[DeleteForm, Depends()],
    user: user_dependency,
    db: db_dependency,
) -> None:
    if form_data.username != user.username:
        raise HTTPException(400, detail="Wrong username")

    if not bcrypt_context.verify(form_data.password, user.password):
        raise HTTPException(400, detail="Incorrect password")

    await db.delete(user)

    try:
        await db.commit()
    except:
        raise HTTPException(500, detail="Failed to delete user from database")


@router.put(
    "/avatar",
    status_code=201,
    dependencies=[Depends(RateLimiter(times=2, seconds=1, identifier=user_identifer))],
)
async def upload_avatar(
    file_request: UploadFile, user: user_dependency, db: db_dependency
) -> None:
    if file_request.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(400, "Unsupported file type")

    try:
        image = Image.open(file_request.file)
        image_bytes = io.BytesIO()
        image.resize((256, 256), Image.LANCZOS).save(image_bytes, format="PNG")
        user.picture = image_bytes.getvalue()
    except:
        raise HTTPException(500, "Failed to process file")
    finally:
        image.close()

    try:
        await db.commit()
    except:
        raise HTTPException(500, detail="Failed to upload new image to database")


@router.delete(
    "/avatar",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=10, seconds=1, identifier=user_identifer))],
)
async def delete_avatar(user: user_dependency, db: db_dependency) -> None:
    user.picture = None

    try:
        await db.commit()
    except:
        raise HTTPException(500, detail="Failed to remove image from database")


@router.patch(
    "/profile",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=10, seconds=1, identifier=user_identifer))],
)
async def edit_user_info(
    edit_user_request: EditUserRequest, user: user_dependency, db: db_dependency
) -> None:
    user.about_me = edit_user_request.about_me
    user.country = edit_user_request.country

    if len(edit_user_request.about_me) > 500:
        raise HTTPException(400, "about_me is greater than maximum characters 500")

    if (user.country is not None) and (user.country not in valid_country_codes):
        raise HTTPException(400, "country is not in valid_country_code")

    try:
        await db.commit()
    except:
        raise HTTPException(500, "Failed to edit user info")


@router.get(
    "/profile",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=10, seconds=1, identifier=user_identifer))],
)
async def get_personal_profile(user: user_dependency):
    return PersonalUserResponse(
        username=user.username,
        email=user.email,
        about_me=user.about_me,
        rating=user.rating,
        country=user.country,
        registration_date=user.registration_date,
    )


@router.get(
    "/profile/{username}",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=10, seconds=1))],
)
async def get_user_profile(username: str, db: db_dependency):
    statement = select(Users).where(Users.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, detail="User does not exist")

    return PublicUserResponse(
        username=user.username,
        about_me=user.about_me,
        rating=user.rating,
        country=user.country,
        registration_date=user.registration_date,
    )


@router.get(
    "/avatar",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=10, seconds=1, identifier=user_identifer))],
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_user_avatar(user: user_dependency):
    if user.picture is None:
        return Response(content=default_pfp, media_type="image/png")

    return Response(content=user.picture, media_type="image/png")


@router.get(
    "/avatar/{username}",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=5, seconds=2))],
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_user_avatar(username: str, db: db_dependency):
    statement = select(Users).where(Users.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, detail="User does not exist")

    if user.picture is None:
        return Response(content=default_pfp, media_type="image/png")

    return Response(content=user.picture, media_type="image/png")
