import base64
import io
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from database import db_dependency
from dotenv import find_dotenv, load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Response, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from jose import ExpiredSignatureError, JWTError, jwt
from jose.constants import ALGORITHMS
from models import Appearance, Users
from passlib.context import CryptContext
from PIL import Image
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.websockets import WebSocket

# Find and parse .env file
load_dotenv(find_dotenv())

# https://github.com/pyca/bcrypt/issues/684
logging.getLogger("passlib").setLevel(logging.ERROR)

router = APIRouter(prefix="/user", tags=["user"])

# Get constants used for hashing from .env file
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

# Check if constants exist in .env file and if algorithm is valid
assert SECRET_KEY, "JWT_SECRET_KEY not found in .env"
assert ALGORITHM, "JWT_ALGORITHM not found in .env"
assert ALGORITHM in ALGORITHMS.SUPPORTED, f"Algorithm {ALGORITHM} not supported"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/user/token")

# Load countries from csv file
with open("countries.csv") as f:
    valid_country_codes = set()
    countries = {}
    for line in f:
        code, name, emoji, image = line.strip().split(",")
        valid_country_codes.add(code)
        countries[code] = {
            "name": name,
            "emoji": emoji,
            "image": image,
            "circular_image": f"https://hatscripts.github.io/circle-flags/flags/{code.lower()}.svg",
        }

# Load default profile picture and convert to base64
with open("default_avatar.png", "rb") as f:
    default_pfp = f.read()
default_pfp_b64 = "data:image/png;base64, " + base64.b64encode(default_pfp).decode()


# --------------- #
# Pydantic models #
# --------------- #


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
    avatar: str | None
    about_me: str | None = Field(min_length=0, max_length=500)
    country: str | None = Field(min_length=2, max_length=2)


class PublicUserResponse(BaseModel):
    username: str = Field(max_length=32)
    admin: bool
    avatar: bytes
    about_me: str | None = Field(min_length=0, max_length=500)
    country: str | None = Field(min_length=2, max_length=2)
    rating: int | None
    registration_date: datetime


class PersonalUserResponse(PublicUserResponse):
    email: str


class Country(BaseModel):
    name: str
    emoji: str
    image: str
    circular_image: str


class CountryResponse(BaseModel):
    countries: dict[str, Country]


# HTTP exception for when user gives wrong login details
invalid_auth = HTTPException(
    status_code=401,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# ---------------- #
# Helper functions #
# ---------------- #


async def get_user(username: str, db: db_dependency) -> Users:
    """
    Fetch user row from database by username
    """
    statement = select(Users).where(Users.username == username)
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
    """
    Get current user by decoding JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str):
            raise invalid_auth

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise invalid_auth

    return await get_user(username, db)


user_dependency = Annotated[Users, Depends(get_current_user)]


async def authenticate_user(
    username: str, password: str, db: AsyncSession
) -> Users | Literal[False]:
    """
    Authenticate user checking if password matches stored hash
    """
    statement = select(Users).where(Users.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str, expires_delta: timedelta) -> str:
    """
    Create JWT token given username and expiration time
    """
    encode = {
        "sub": username,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def user_identifer(request: Request | WebSocket) -> str:
    """
    Identify user for ratelimiting requests
    """
    token = request.headers.get("Authorization")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: int = payload.get("sub")
        if username is not None:
            return username
    except:
        pass

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host + ":" + request.scope["path"]


def user_picture_B64(picture: bytes | None):
    """
    Convert image bytes to base64
    If picture is None return the default profile picture in b64
    """
    return (
        default_pfp_b64
        if picture is None
        else "data:image/png;base64, " + base64.b64encode(picture).decode()
    )


# ------------- #
# API Endpoints #
# ------------- #


@router.post(
    "/", status_code=201, dependencies=[Depends(RateLimiter(times=3, minutes=1))]
)
async def create_user(
    form_data: Annotated[SignupForm, Depends()],
    db: db_dependency,
) -> None:
    """
    Create a user account from username, email and password
    """
    if not all(c.isalnum() for c in form_data.username):
        raise HTTPException(
            422, detail="Username should only contain alphanumeric characters"
        )

    if len(form_data.password) < 6:
        raise HTTPException(422, detail="Password should be at least 6 characters long")

    statement = select(Users).where(Users.username == form_data.username)
    result = await db.execute(statement=statement)

    if result.scalar_one_or_none() is not None:
        raise HTTPException(400, "Someone already has that username")

    statement = select(Users).where(Users.email == form_data.email)
    result = await db.execute(statement=statement)

    if result.scalar_one_or_none() is not None:
        raise HTTPException(400, "Someone already has that email")

    create_user_model = Users(
        username=form_data.username,
        email=form_data.email,
        password=bcrypt_context.hash(form_data.password),
        registration_date=datetime.now(),
    )

    create_appearance_model = Appearance(username=form_data.username)

    db.add(create_user_model)
    db.add(create_appearance_model)
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
    """
    Login by getting a JWT token
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(401, detail="Could not validate user")

    token = create_access_token(user.username, timedelta(weeks=1))

    return {"access_token": token, "token_type": "bearer"}


@router.delete(
    "/", status_code=200, dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def delete_user(
    form_data: Annotated[DeleteForm, Depends()],
    user: user_dependency,
    db: db_dependency,
) -> None:
    """
    Delete account requiring username and password
    """
    if form_data.username != user.username:
        raise HTTPException(400, detail="Wrong username")

    if not bcrypt_context.verify(form_data.password, user.password):
        raise HTTPException(400, detail="Incorrect password")

    await db.delete(user)
    await db.execute("DELETE appearance WHERE username = ?", (user.username,))

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
    """
    Upload a profile picture for account
    """
    if file_request.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(400, "Unsupported file type")

    try:
        # Resize image to 256x256 and convert back to bytes before saving to database
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
    """
    Remove profile picture
    """
    if not user.picture:
        raise HTTPException(404, detail="You do not have a profile picture")

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
    """
    Edit user information (avatar, about_me, country)
    """

    if edit_user_request.avatar == default_pfp_b64[22:]:
        user.picture = None
    elif edit_user_request.avatar is not None:
        try:
            image = Image.open(
                io.BytesIO(base64.decodebytes(bytes(edit_user_request.avatar, "utf-8")))
            )
            image_bytes = io.BytesIO()

            # Resize image to 256x256 after cropping so that image is not stretched
            width, height = image.size
            crop_size = min(image.size)
            image = image.crop(
                (
                    (width - crop_size) // 2,
                    (height - crop_size) // 2,
                    (width + crop_size) // 2,
                    (height + crop_size) // 2,
                )
            )
            image.resize((256, 256), Image.LANCZOS).save(image_bytes, format="PNG")
            user.picture = image_bytes.getvalue()
        except Exception:
            raise HTTPException(500, "Failed to process file")
        finally:
            image.close()

    user.about_me = edit_user_request.about_me
    user.country = edit_user_request.country

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
    """
    Return account information of current user
    """
    return PersonalUserResponse(
        username=user.username,
        admin=user.admin,
        avatar=user_picture_B64(user.picture),
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
    """
    Return public account information given username
    """
    statement = select(Users).where(Users.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, detail="User does not exist")

    return PublicUserResponse(
        username=user.username,
        admin=user.admin,
        avatar=user_picture_B64(user.picture),
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
async def get_personal_avatar(user: user_dependency):
    """
    Return profile picture of current user
    """
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
    """
    Return profile picture of account given username
    """
    statement = select(Users).where(Users.username == username)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, detail="User does not exist")

    if user.picture is None:
        return Response(content=default_pfp, media_type="image/png")

    return Response(content=user.picture, media_type="image/png")


@router.get("/countries", status_code=200)
async def get_available_countries():
    """
    Returns available countries that can be used in a user profile
    """
    return CountryResponse(countries=countries)


@router.get("/default_avatar", status_code=200)
async def get_available_countries():
    """
    Returns default avatar
    """
    return default_pfp_b64
