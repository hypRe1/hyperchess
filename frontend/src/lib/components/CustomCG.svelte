<script lang="ts">
	import { Chessground } from 'svelte-chessground';
	import { Chess } from 'chess.js';
	import { onMount } from 'svelte';
	import { legalMoves } from '$lib/util';
	export let piece: string;
	export let board: string;
	export let config;
	import '$lib/board-themes/base.css';
	import '$lib/board-themes/custom.css';

	export let chess = new Chess();
	export let chessground: Chessground;
	let assigned: boolean = false;

	onMount(async () => {
		assigned = true;
	});

	export function undo() {
		if (assigned) {
			chess.undo();
			const moveHistory = chess.history({ verbose: true });
			let lastMove = undefined;
			if (moveHistory.length != 0) {
				lastMove = [
					moveHistory[moveHistory.length - 1].from,
					moveHistory[moveHistory.length - 1].to
				];
			}

			const colour = chess.turn() == 'w' ? 'white' : 'black';

			chessground.set({
				fen: chess.fen(),
				turnColor: colour,
				check: chess.isCheck(),
				lastMove: lastMove,
				movable: {
					color: colour,
					dests: legalMoves(chess)
				}
			});
		}
		return;
	}

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
				turnColor: 'white',
				check: false,
				selected: undefined,
				lastMove: undefined,
				movable: {
					color: 'white',
					dests: legalMoves(chess)
				}
			});
		}
	}

	export function load_fen(fen: string) {
		if (assigned) {
			chess = new Chess(fen);
			const colour = chess.turn() == 'w' ? 'white' : 'black';
			chessground.set({
				fen: chess.fen(),
				turnColor: colour,
				check: chess.isCheck(),
				selected: undefined,
				lastMove: undefined,
				movable: {
					color: colour,
					dests: legalMoves(chess)
				}
			});
		}
	}
</script>

<Chessground class="cg-base piece-{piece} board-{board}" bind:this={chessground} {config} />
