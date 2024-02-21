import random
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from routers.user import user_dependency

router = APIRouter(prefix="/match", tags=["match-listing"])


class MatchListing(BaseModel):
    colour: bool | None
    time: int
    bonus: int | None

    handicapped: bool
    opp_time: int | None
    opp_bonus: int | None


class MatchListingRequestForm(BaseModel):
    private: bool
    colour: bool | None
    time: int
    bonus: int | None

    opp_time: bool
    opp_time: int | None
    opp_bonus: int | None


available_matches: dict[str, MatchListing] = {}
private_matches: dict[str, MatchListing] = {}


@router.post("/", status_code=201)
async def create_match(
    form_data: MatchListingRequestForm, user: user_dependency
) -> None:
    """
    Create a match listing
    """
    if user.username in available_matches.keys():
        raise HTTPException(403, "You have already created a public match")

    if user.username in private_matches.keys():
        raise HTTPException(403, "You have already created a private match")

    match_listing = MatchListing(
        colour=form_data.colour,
        time=form_data.time,
        bonus=form_data.bonus,
        handicapped=(form_data.opp_time != form_data.time)
        or (form_data.opp_bonus != form_data.opp_bonus),
        opp_time=form_data.opp_time,
        opp_bonus=form_data.opp_bonus,
    )

    if form_data.private:
        private_matches[user.username] = match_listing
    else:
        available_matches[user.username] = match_listing


@router.delete("/", status_code=200)
async def delete_match(user: user_dependency) -> None:
    """
    Delete a match listing that you have created
    """
    if available_matches.get(user.username) is not None:
        del available_matches[user.username]

    elif available_matches.get(user.username) is not None:
        del private_matches[user.username]

    else:
        raise HTTPException(404, detail="Match not found")


@router.get("/", status_code=200)
async def get_matches() -> dict[str, MatchListing]:
    """
    Returns dictionary mapping username to match listing
    """
    return available_matches


@router.post("/accept", status_code=200)
async def join_match():
    """
    Accept a match listing
    """
    raise HTTPException(501)
