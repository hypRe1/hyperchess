<script lang="ts">
    import { Chessground } from "svelte-chessground";
    import { Chess, type Move } from "chess.js";
    import { onMount } from "svelte";
    import { legalMoves, makeEngineMove } from "$lib/util";
    import "$lib/board-themes/base.css";
    import "$lib/board-themes/pieces.css";
    import "$lib/board-themes/board.css";
    export let depth: number;
    export let engine: string;

    let chess = new Chess();
    let chessground: Chessground;
    let assigned: boolean = false;

    let config = {
        animation: {
            enabled: true,
            duration: 300,
        },

        movable: {
            color: "white",
            free: false,
            dests: legalMoves(chess),
            showDests: true,
        },
        highlight: {
            check: true,
        },
        coordinates: true,
    };

    onMount(async () => {
        assigned = true;
        chessground.set({
            movable: {
                events: {
                    after: makeEngineMove(chessground, chess, depth, engine),
                },
            },
        });
    });

    export function undo() {
        if (assigned) {
            chess.undo();
            const moveHistory = chess.history({ verbose: true });
            let lastMove = undefined;
            if (moveHistory.length != 0) {
                lastMove = [
                    moveHistory[moveHistory.length - 1].from,
                    moveHistory[moveHistory.length - 1].to,
                ];
            }

            const colour = chess.turn() == "w" ? "white" : "black";

            chessground.set({
                fen: chess.fen(),
                turnColor: colour,
                check: chess.isCheck(),
                lastMove: lastMove,
                movable: {
                    color: colour,
                    dests: legalMoves(chess),
                },
            });
        }
        return;
    }

    // export function history(): Move[] | undefined {
    //     if (assigned) {
    //         return chess.history({ verbose: true });
    //     }
    // }

    export function flipBoard() {
        if (assigned) {
            chessground.toggleOrientation();
        }
    }

    export function reset() {
        if (assigned) {
            chess = new Chess();
            chessground.set({
                fen: chess.fen(),
                turnColor: "white",
                check: false,
                selected: undefined,
                lastMove: undefined,
                movable: {
                    color: "white",
                    dests: legalMoves(chess),
                },
            });
        }
    }

    export function load_fen(fen: string) {
        if (assigned) {
            chess = new Chess(fen);
            const colour = chess.turn() == "w" ? "white" : "black";
            chessground.set({
                fen: chess.fen(),
                turnColor: colour,
                check: chess.isCheck(),
                selected: undefined,
                lastMove: undefined,
                movable: {
                    color: colour,
                    dests: legalMoves(chess),
                },
            });
        }
    }

    $: {
        if (assigned) {
            chessground.set({
                movable: {
                    events: {
                        after: makeEngineMove(
                            chessground,
                            chess,
                            depth,
                            engine,
                        ),
                    },
                },
            });
        }
    }
</script>

<Chessground
    class="cg-base cg-pieces cg-board"
    bind:this={chessground}
    {config}
/>
