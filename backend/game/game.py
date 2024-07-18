import chess


class Game:
    def __init__(self, fen: str) -> None:
        self.board = chess.Board(fen)
        self.history = []

    def make_move(self, move_uci: str) -> bool:
        try:
            move = chess.Move.from_uci()
            if move in self.board.legal_moves:
                self.board.push(move)
                self.history.append(move)
                return {"success": True}
            else:
                return {"success": False, "details": "Illegal move!"}
        except ValueError:
            return {"success": False, "details": "Invalid move format! Use UCI format."}

    def undo_move(self):
        self.board.pop()
