import datetime
import random

from database import db_dependency
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from models import Matches, UserMatches
from pydantic import BaseModel, Field, ValidationError
from routers.user import user_dependency
from sqlalchemy import select
from util.gameCompressor import compress, decompress
from util.gameConnectionManager import GameConnectionManager, MatchListingRequestForm

router = APIRouter(prefix="/match", tags=["match-listing"])
manager = GameConnectionManager()


class Match(BaseModel):
    white: str
    black: str
    moves: list[str]
    winner: bool
    result: int
    time_started: datetime.datetime = Field(default_factory=datetime.datetime.now)


@router.post(
    "/",
    status_code=200,
)
async def add_match(request: Match, user: user_dependency, db: db_dependency):
    try:
        compressed_moves = compress(request.moves)
    except ValueError:
        raise HTTPException(400, detail="Cannot process illegal move")

    match_id = random.randint(0, 2000000000)

    create_match_model = Match(
        id=match_id,
        white=request.white,
        black=request.black,
        moves=compressed_moves,
        winner=request.winner,
        result=request.result,
        time_started=request.time_started,
        hyperchess=False,
    )

    create_user_match_model = UserMatches(username=user.username, matchId=match_id)

    db.add(create_match_model)
    db.add(create_user_match_model)
    try:
        await db.commit()
    except Exception:
        raise HTTPException(500, detail="Failed to add match to database")


@router.get(
    "/",
    status_code=200,
)
async def get_match(id: int, db: db_dependency):
    statement = select(Matches).filter_by(id=id)
    result = await db.execute(statement=statement)

    match_model = result.scalar_one_or_none()
    if match_model is None:
        raise HTTPException(404, detail="Match does not exist")

    try:
        moves = [m.uci() for m in decompress(match_model.moves).move_stack]
    except IndexError:
        raise HTTPException(500, detail="Failed to decompress match moves")

    return Match(
        white=match_model.white,
        black=match_model.black,
        moves=moves,
        winner=match_model.winner,
        result=match_model.result,
    )


@router.websocket("/ws")
async def match(websocket: WebSocket):
    """
    Match websocket
    """
    user = await manager.connect(websocket)
    if user is None:
        return
    try:
        while True:
            data = await websocket.receive_json()
            cmd = data[0]
            match cmd:
                case "addListing":
                    try:
                        form = MatchListingRequestForm.model_validate(data[1])
                    except ValidationError as e:
                        await manager.send_personal_message(
                            user.username,
                            ["addListing", {"success": False, "details": str(e)}],
                        )
                    await manager.add_listing(form, user.username)
                case "removeListing":
                    await manager.remove_listing(user.username)
                case "acceptListing":
                    await manager.accept_listing(data[1], user.username)

                case "listenListings":
                    await manager.add_listing_listener(user.username)
                case "listenMatches":
                    await manager.add_match_listener(user.username)
                case "stopListenListings":
                    await manager.remove_listing_listener(user.username)
                case "stopListenMatches":
                    await manager.remove_match_listener(user.username)

                case "joinMatch":
                    await manager.join_game(user.username, data[1])
                case "makeMove":
                    await manager.make_move(user.username, data[1])
                case "resign":
                    await manager.resign(user.username)
                case "draw":
                    await manager.draw(user.username, data[1])
                case "chat":
                    pass
                case "checkClock":
                    await manager.check_clock(user.username)
    except WebSocketDisconnect:
        await manager.disconnect(user.username, websocket)
