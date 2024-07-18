<script lang="ts">
    import { Chessground } from "svelte-chessground";
    import CustomCG from "$lib/components/CustomCG.svelte";
    import { Chess } from "chess.js";
    import { onMount } from "svelte";
    import { legalMoves, makeEngineMove } from "$lib/util";

    export let depth: number;
    export let engine: string;
    export let piece: string;
    export let board: string;

    export let undo: () => void;
    export let flipBoard: () => void;
    export let reset: () => void;
    export let load_fen: (fen: string) => void;

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
    });

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

<CustomCG
    bind:chessground
    bind:chess
    bind:undo
    bind:flipBoard
    bind:reset
    bind:load_fen
    bind:piece
    bind:board
    {config}
/>
