import json
import os
from enum import StrEnum

from database import db_dependency
from fastapi import APIRouter, HTTPException
from models import Appearance
from pydantic import BaseModel
from routers.user import user_dependency
from sqlalchemy import select

router = APIRouter(prefix="/appearance", tags=["appearance"])


class Themes(StrEnum):
    SKELETON = "skeleton"
    WINTRY = "wintry"
    MODERN = "modern"
    ROCKET = "rocket"
    SEAFORM = "seafoam"
    VINTAGE = "vintage"
    SAHARA = "sahara"
    HAMLINDIGO = "hamlindigo"
    GOLD_NOUVEAU = "gold-nouveau"
    CRIMSON = "crimson"
    HYPERTHEME = "hypertheme"


BOARD_THEMES_PATH = "../frontend/static/"

# Get boards and pieces from path
board_files = []
for f in os.listdir(BOARD_THEMES_PATH + "board"):
    if not (f.endswith(".jpg") or f.endswith(".png")) or f.count(".") > 1:
        continue
    board_files.append(f.removesuffix(".jpg").removesuffix(".png"))

for f in os.listdir(BOARD_THEMES_PATH + "board/svg"):
    if not f.endswith(".svg"):
        continue
    board_files.append(f.removesuffix(".svg"))

Boards = StrEnum("Boards", {b.replace("-", "_").upper(): b for b in board_files})
Pieces = StrEnum(
    "Pieces",
    {p.replace("-", "_").upper(): p for p in os.listdir(BOARD_THEMES_PATH + "pieces")},
)

appearances = {
    "themes": [t.value for t in Themes],
    "boards": [b.value for b in Boards],
    "pieces": [p.value for p in Pieces],
}
with open(f"{BOARD_THEMES_PATH}appearances.json", "w") as fp:
    json.dump(appearances, fp)


class UserAppearance(BaseModel):
    theme: Themes
    board: Boards  # type: ignore
    piece: Pieces  # type: ignore
    dark: bool


# ------------- #
# API Endpoints #
# ------------- #


@router.get("/")
async def get_appearance(user: user_dependency, db: db_dependency) -> UserAppearance:
    """
    Get user's theme and name of board and pieces for cg styling
    """
    statement = select(Appearance).where(Appearance.username == user.username)
    result = await db.execute(statement)
    appearance = result.scalar_one_or_none()
    return UserAppearance(
        theme=appearance.theme,
        board=appearance.board,
        piece=appearance.piece,
        dark=appearance.dark,
    )


@router.patch("/")
async def edit_appearance(
    user: user_dependency, db: db_dependency, apperance_request: UserAppearance
):
    """
    Edit user's theme and name of board and pieces for cg styling
    """
    statement = select(Appearance).where(Appearance.username == user.username)
    result = await db.execute(statement)
    appearance = result.scalar_one_or_none()
    appearance.theme = apperance_request.theme
    appearance.board = apperance_request.board
    appearance.piece = apperance_request.piece
    appearance.dark = apperance_request.dark

    try:
        await db.commit()
    except:
        raise HTTPException(500, "Failed to edit user appearance")


@router.get("/boards")
async def get_boards():
    """Get boards"""
    return [b.value for b in Boards]


@router.get("/pieces")
async def get_boards():
    """Get pieces"""
    return [p.value for p in Pieces]


@router.get("/themes")
async def get_boards():
    """Get themes"""
    return [t.value for t in Themes]
