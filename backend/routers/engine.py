import os

import chess
import chess.engine
from database import db_dependency
from fastapi import APIRouter, Depends, HTTPException
from fastapi_limiter.depends import RateLimiter
from models import Matches
from pydantic import BaseModel, ConfigDict, Field, field_validator
from routers.user import user_dependency
from sqlalchemy import select
from util.gameCompressor import decompress_moves

router = APIRouter(prefix="/engine", tags=["engine"])

# Get engine directory containing engine executables from .env file
ENGINES_LOC = os.getenv("ENGINES_LOC")
assert ENGINES_LOC, "ENGINES_LOC not found in .env"

engine_locs = {
    file: os.path.join(ENGINES_LOC, file) for file in os.listdir(ENGINES_LOC)
}

# lc0 installed through homebrew
# engine_locs["Lc0"] = "lc0"

# WEIGHTS_LOC = os.getenv("WEIGHTS_LOC")
# assert WEIGHTS_LOC, "WEIGHTS_LOC not found in .env"

# for file in os.listdir(WEIGHTS_LOC):
#     engine_locs[f"Lc0 - {file}"] = f"lc0 --weights {os.path.join(ENGINES_LOC, file)}"

# --------------- #
# Pydantic models #
# --------------- #


class BestMoveRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    fen: str
    engine: str
    depth: int = Field(default=6, lt=21, gt=0)

    @field_validator("engine")
    @classmethod
    def engine_available(cls, engine: str):
        if (engine_loc := engine_locs.get(engine)) is None:
            raise ValueError(f"Engine '{engine}' not available")
        return engine_loc


class ReviewMatchRequest(BaseModel):
    engine: str
    match_id: int
    depth: int = Field(default=4, lt=20, gt=0)

    @field_validator("engine")
    @classmethod
    def engine_available(cls, engine: str):
        if (engine_loc := engine_locs.get(engine)) is None:
            raise ValueError(f"Engine '{engine}' not available")
        return engine_loc


class ReviewMatchResponse(BaseModel):
    time: str


# ------------- #
# API Endpoints #
# ------------- #


@router.post(
    "/",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=3, seconds=1))],
)
async def best_move(best_move_request: BestMoveRequest):
    """
    Return uci string for top engine move given position, the engine and depth
    """
    _, engine = await chess.engine.popen_uci(best_move_request.engine)
    result = await engine.play(
        chess.Board(best_move_request.fen),
        chess.engine.Limit(depth=best_move_request.depth),
    )
    await engine.quit()
    return result.move.uci()


@router.post("/eval", status_code=200)
async def position_evaluation(best_move_request: BestMoveRequest):
    """
    Return engine score of position
    """
    _, engine = await chess.engine.popen_uci(best_move_request.engine)
    board = chess.Board(best_move_request.fen)
    info = await engine.analyse(
        board, chess.engine.Limit(depth=best_move_request.depth)
    )
    await engine.quit()
    return info


@router.post("/review_match", status_code=200)
async def review_match(
    request: ReviewMatchRequest, user: user_dependency, db: db_dependency
):
    """
    Review match
    """
    _, engine = await chess.engine.popen_uci(request.engine)
    statement = select(Matches).filter_by(id=request.match_id)
    result = await db.execute(statement=statement)
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(404, detail="Match does not exist")

    moves = decompress_moves(match.moves)
    analysis = []

    copy = chess.Board()

    async def review_pos():
        info = await engine.analyse(copy, chess.engine.Limit(depth=request.depth))
        pv = info.get("pv")
        best_move = None
        if pv is not None and len(pv) > 0:
            best_move = pv[0].uci()
        score = info.get("score")
        white_score = score.white()
        white_cp = white_score.score()
        white_mate = white_score.mate()

        if white_mate is not None:
            label = "Mate in " + str(white_mate)
            per = 100 if (white_mate > 0) else -100
        elif white_cp is not None:
            label = str(white_cp / 100)
            per = (white_cp / 25) + 50
        else:
            per = 69
            label = "on skibidi"

        analysis.append(
            {
                "best": best_move,
                "pv": pv,
                "score": {
                    "per": per,
                    "label": label,
                },
            }
        )

    await review_pos()
    for move in moves:
        copy.push_san(move)
        await review_pos()

    await engine.quit()
    return analysis


@router.get(
    "/available",
    status_code=200,
    dependencies=[Depends(RateLimiter(times=3, seconds=1))],
)
async def available_engines():
    """
    Returns tuple of available engines
    """
    return tuple(engine_locs.keys())
