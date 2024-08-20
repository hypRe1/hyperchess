import { Chessground } from "svelte-chessground";
import { Chess, type Square, SQUARES } from 'chess.js';
import { sendMessage } from '$lib/stores/websocket';

export function legalMoves(chess: Chess) {
    const dests = new Map();
    SQUARES.forEach(s => {
        const ms = chess.moves({ square: s, verbose: true });
        if (ms.length) dests.set(s, ms.map(m => m.to));
    });
    return dests;
}

export function makeEngineMove(chessground: Chessground, chess: Chess, depth: number, engine: string) {
    return async (orig: Square, dest: Square) => {
        const promotion = chess.get(orig).type == 'p' && (dest.charAt(1) == '1' || dest.charAt(1) == '8') ? "q" : undefined;
        const move_chessjs = chess.move({ from: orig, to: dest, promotion });
        if (move_chessjs.flags.includes('e') || move_chessjs.flags.includes('p')) {
            chessground.set({ fen: chess.fen() })
        }

        chessground.set({
            check: chess.isCheck()
        });

        const response = await fetch('http://127.0.0.1:8000/api/engine/', {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'fen': chess.fen(),
                'engine': engine,
                'depth': depth
            })
        });

        if (response.ok) {
            const move = (await response.text()).slice(1, -1)
            console.log(move)
            const move_chessjs = chess.move(move)


            // reload chessground fen if there is enpassant or promotion
            if (move_chessjs.flags.includes('e') || move_chessjs.flags.includes('p')) {
                chessground.set({ fen: chess.fen() })
            } else {
                chessground.move(move_chessjs.from, move_chessjs.to);
            }


            const colour = chess.turn() == "w" ? "white" : "black";
            chessground.set({
                turnColor: colour,
                check: chess.isCheck(),
                movable: {
                    color: colour,
                    dests: legalMoves(chess),
                },
            });
            chessground.playPremove();
        }
    };
}

export function makePlayerMove(chessground: Chessground, chess: Chess) {
    return async (orig: Square, dest: Square) => {
        const promotion = chess.get(orig).type == 'p' && (dest.charAt(1) == '1' || dest.charAt(1) == '8') ? "q" : undefined;
        const move_chessjs = chess.move({ from: orig, to: dest, promotion });
        sendMessage(JSON.stringify(['makeMove', move_chessjs.from + move_chessjs.to + ((move_chessjs.promotion === undefined) ? "" : promotion)]));
        if (move_chessjs.flags.includes('e') || move_chessjs.flags.includes('p')) {
            chessground.set({ fen: chess.fen() })
        }

        chessground.set({
            check: chess.isCheck(),
        });
    };
}