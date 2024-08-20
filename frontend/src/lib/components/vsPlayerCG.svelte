<script lang="ts">
	import { Chessground } from 'svelte-chessground';
	import CustomCG from '$lib/components/CustomCG.svelte';
	import { Chess } from 'chess.js';
	import { onMount } from 'svelte';
	import { legalMoves, makePlayerMove } from '$lib/util';

	enum BoardMode {
		white,
		black,
		spectate
	}

	export let piece: string;
	export let board: string;
	export let mode: BoardMode;

	export let flipBoard: () => void;

	export function push_move(
		move:
			| string
			| {
					from: string;
					to: string;
					promotion?: string;
			  }
	) {
		if (assigned) {
			const move_chessjs = chess.move(move);
			if (move_chessjs.flags.includes('e') || move_chessjs.flags.includes('p')) {
				chessground.set({ fen: chess.fen() });
			} else {
				chessground.move(move_chessjs.from, move_chessjs.to);
			}
			console.log(chess.turn());
			chessground.set({
				turnColor: chess.turn() == 'w' ? 'white' : 'black',
				check: chess.isCheck(),
				movable: {
					dests: legalMoves(chess)
				}
			});
		}
	}

	let chess = new Chess();
	let chessground: Chessground;
	let assigned: boolean = false;

	let config = {
		animation: {
			enabled: true,
			duration: 300
		},

		movable: {
			color: 'white',
			free: false,
			dests: legalMoves(chess),
			showDests: true
		},
		highlight: {
			check: true
		},
		coordinates: true
	};

	onMount(async () => {
		assigned = true;
	});

	$: {
		if (assigned) {
			chessground.set({
				orientation: mode == BoardMode.black ? 'black' : 'white',
				// viewOnly: mode == BoardMode.black,
				movable: {
					color: mode == BoardMode.black ? 'black' : 'white',
					events: {
						after: makePlayerMove(chessground, chess)
					}
				}
			});
			console.log(chessground.getState());
		}
	}
</script>

<CustomCG bind:chessground bind:chess bind:flipBoard bind:piece bind:board {config} />
