import os
from enum import StrEnum

import chess
import chess.engine
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

router = APIRouter(prefix="/engine")

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

    @computed_field
    @property
    def board(self) -> chess.Board:
        return chess.Board(self.fen)


@router.post("/", status_code=200)
async def best_move(best_move_request: BestMoveRequest):
    _, engine = await chess.engine.popen_uci(best_move_request.engine)
    result = await engine.play(
        best_move_request.board, chess.engine.Limit(depth=best_move_request.depth)
    )
    await engine.quit()
    return result.move.uci()


@router.get("/available", status_code=200)
async def available_engines():
    return tuple(engine_locs.keys())
