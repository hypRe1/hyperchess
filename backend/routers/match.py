from typing import List

from fastapi import APIRouter

router = APIRouter(prefix="/match", tags=["match"])


class MatchListing:
    id: int
    player_id: int
    colour: bool | None
    time: int
    bonus: int | None

    handicapped: bool
    opp_time: int | None
    opp_bonus: int | None


available_matches: List[MatchListing] = []


async def create_match():
    pass


async def delete_match():
    pass


async def join_match():
    pass


async def get_matches():
    pass
