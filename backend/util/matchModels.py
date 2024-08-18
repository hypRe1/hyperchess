import time as t
from dataclasses import dataclass

import chess
from pydantic import BaseModel, Field


class MatchModel(BaseModel):
    code: str
    public: bool
    white_player: str | None
    black_player: str | None
    time: int
    bonus: int
    connected: list[str]
    board: str
    game_over: bool = False
    result: str | None = None
    time_created: int = Field(default_factory=t.time)
    time_ended: int | None = Field(None)


@dataclass
class Match:
    code: str
    public: bool
    white_player: str | None
    black_player: str | None
    time: int
    bonus: int
    connected: set[str]
    board = chess.Board()
    game_over: bool = False
    result: str | None = None
    time_created: int = int(t.time())
    time_ended: int | None = None

    def to_match_model(self) -> MatchModel:
        return MatchModel(
            code=self.code,
            public=self.public,
            white_player=self.white_player,
            black_player=self.black_player,
            time=self.time,
            bonus=self.bonus,
            connected=self.connected,
            board=self.board.fen(),
            game_over=self.game_over,
            result=self.result,
            time_created=self.time_created,
            time_ended=self.time_ended,
        )
