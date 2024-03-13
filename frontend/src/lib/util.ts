/*
 * Helper functions for some examples
 */

import { Chess, SQUARES } from 'chess.js';
import type { Square } from 'chess.js'
import type { Chessground } from 'svelte-chessground';


// Find all legal moves
export function toDests(chess: Chess) {
    const dests = new Map();
    SQUARES.forEach(s => {
        const ms = chess.moves({ square: s, verbose: true });
        if (ms.length) dests.set(s, ms.map(m => m.to));
    });
    return dests;
}

// Play a move and toggle whose turn it is
export function playOtherSide(chessground: Chessground, chess: Chess) {
    return (orig: Square, dest: Square) => {
        chess.move({ from: orig, to: dest });
        const color = chess.turn() == 'w' ? 'white' : 'black';
        chessground.set({
            turnColor: color,
            movable: {
                color: color,
                dests: toDests(chess)
            }
        });
    };
}