import time as t
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

import chess
from pydantic import BaseModel, Field, field_serializer


class Result(IntEnum):
    ONGOING = 0
    CHECKMATE = 1
    RESIGN = 2
    FLAGGED = 3
    STALEMATE = 4
    INSUFFICIENT_MATERIAL = 5
    REPETITION = 6
    SEVENTYFIVE_MOVES = 7


class MatchModel(BaseModel):
    code: str
    public: bool
    white_player: str
    black_player: str
    time: float
    bonus: int
    connected: list[str]
    moves: list[str]
    game_over: bool = False
    result: Result = Result.ONGOING
    winner: bool | None = None
    time_created: int = Field(default_factory=t.time)
    timings: List[float] = Field(default_factory=list)

    @field_serializer("result")
    def serialize_result(result: Result):
        return int(result)


@dataclass
class Match:
    code: str
    public: bool
    white_player: str
    black_player: str
    time: float
    bonus: int
    connected: set[str]
    board: chess.Board = field(default_factory=chess.Board)
    game_over: bool = False
    result: Result = Result.ONGOING
    winner: bool | None = None
    time_created: int = field(default_factory=lambda: int(t.time()))
    timings: list[float] = field(default_factory=list)

    def to_match_model(self) -> MatchModel:
        return MatchModel(
            code=self.code,
            public=self.public,
            white_player=self.white_player,
            black_player=self.black_player,
            time=self.time,
            bonus=self.bonus,
            connected=self.connected,
            moves=[m.uci() for m in self.board.move_stack],
            game_over=self.game_over,
            result=self.result,
            winner=self.winner,
            time_created=self.time_created,
            timings=self.timings,
        )
