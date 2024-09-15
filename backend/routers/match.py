import datetime
import random

from database import db_dependency
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from models import Matches, UserMatches
from pydantic import BaseModel, Field, ValidationError
from routers.user import user_dependency
from sqlalchemy import select
from util.gameCompressor import compress, decompress_board, decompress_moves
from util.gameConnectionManager import GameConnectionManager, MatchListingRequestForm

router = APIRouter(prefix="/match", tags=["match"])

# Instantiate game connection manager for match websocket connections
manager = GameConnectionManager()

# --------------- #
# Pydantic models #
# --------------- #


class MatchRequest(BaseModel):
    white: str
    black: str
    moves: list[str]
    winner: bool
    result: int
    time: int
    bonus: int
    time_started: datetime.datetime = Field(default_factory=datetime.datetime.now)


class MatchResponse(MatchRequest):
    id: int
    hyperchess: bool


class MatchesResponse(BaseModel):
    id: int
    white: str
    black: str
    n_moves: int
    fen: str
    winner: bool
    result: int
    time: int
    bonus: int
    time_started: datetime.datetime = Field(default_factory=datetime.datetime.now)
    hyperchess: bool


# ------------- #
# API Endpoints #
# ------------- #


@router.post(
    "/",
    status_code=201,
)
async def add_match(request: MatchRequest, user: user_dependency, db: db_dependency):
    """
    Add match to database after compressing moves
    """
    try:
        compressed_moves = compress(request.moves)
    except ValueError:
        raise HTTPException(400, detail="Cannot process illegal move")

    # Randomly generate a unique match id
    match_id = random.randint(1000000000, 2000000000)

    create_match_model = Matches(
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
    "/{id}",
    status_code=200,
)
async def get_match(id: int, db: db_dependency):
    """
    Return all match details given the match id
    """
    statement = select(Matches).filter_by(id=id)
    result = await db.execute(statement=statement)

    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(404, detail="Match does not exist")

    return MatchResponse(
        id=match.id,
        white=match.white,
        black=match.black,
        moves=decompress_moves(match.moves),
        winner=match.winner,
        hyperchess=match.hyperchess,
        time=match.time,
        bonus=match.bonus,
        result=match.result,
    )


@router.get("/", status_code=200)
async def get_matches(user: user_dependency, db: db_dependency):
    """
    Return all matches that a user has either played or added

    Each returned match contains the last board position in FEN notation
    instead of a list of moves like the get_match endpoint
    """
    statement = (
        select(Matches)
        .join(UserMatches, Matches.id == UserMatches.matchId)
        .where(UserMatches.username == user.username)
        .order_by(Matches.time_started.desc())
    )

    result = await db.execute(statement)
    compressedMatches = result.scalars().all()
    decompressedMatches = []
    for match in compressedMatches:
        board = decompress_board(match.moves)
        decompressedMatches.append(
            MatchesResponse(
                id=match.id,
                white=match.white,
                black=match.black,
                n_moves=len(board.move_stack),
                fen=board.fen(),
                winner=match.winner,
                result=match.result,
                hyperchess=match.hyperchess,
                time=match.time,
                bonus=match.bonus,
                time_started=match.time_started,
            )
        )

    return decompressedMatches


@router.websocket("/ws")
async def match(websocket: WebSocket):
    """
    Match websocket used for playing games, listening for match listings and for matches being played
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
