import chess


def compress(moves: list[chess.Move | str]):
    """
    Compress moves to bytes by enumerating legal moves
    """
    compressed = bytearray()
    copy = chess.Board()
    for move in moves:
        if isinstance(move, str):
            move = chess.Move.from_uci(move)
        n = list(copy.legal_moves).index(move)
        compressed.append(n)
        copy.push(move)
    return compressed


def decompress_board(compressed: bytearray):
    """
    Decompress moves returning board object
    """
    board = chess.Board()
    for b in compressed:
        move = list(board.legal_moves)[b]
        board.push(move)
    return board


def decompress_moves(compressed: bytearray):
    """
    Decompress moves returning moves object
    """
    moves = []
    board = chess.Board()
    for b in compressed:
        move = list(board.legal_moves)[b]
        moves.append(board.san(move))
        board.push(move)
    return moves
