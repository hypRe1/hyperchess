<script lang="ts">
	import CustomCG from '$lib/components/CustomCG.svelte';
	import { Chess, type Move } from 'chess.js';
	import { onMount } from 'svelte';
	import { Chessground } from 'svelte-chessground';

	export let piece: string;
	export let board: string;
	export let moves: string[];
	export let highlights: string[] | undefined;

	let moveHistory: Move[];
	let checks: boolean[] = [];

	let positions: string[];
	export let flipBoard: () => void;

	export function set(pos: number) {
		if (assigned) {
			chessground.set({ fen: positions[pos], highlight: { lastMove: false, check: false } });

			if (pos != 0) {
				let lastMove = undefined;
				if (moveHistory.length != 0) {
					lastMove = [moveHistory[pos - 1].from, moveHistory[pos - 1].to];
					console.log(lastMove);
					chessground.set({
						highlight: { lastMove: true, check: true },
						check: checks[pos - 1],
						lastMove: lastMove
					});
					if (highlights !== undefined) {
						chessground.setShapes([
							{
								// @ts-ignore
								orig: highlights[pos - 1].slice(0, 2),
								// @ts-ignore
								dest: highlights[pos - 1].slice(2),
								brush: 'red'
							}
						]);
					}
				}
			}
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

		viewOnly: true,
		coordinates: true
	};

	onMount(async () => {
		let board = new Chess();
		positions = [board.fen()];
		for (var i = 0; i < moves.length; i++) {
			board.move(moves[i]);
			positions.push(board.fen());
			checks.push(board.isCheck());
		}
		assigned = true;
		moveHistory = board.history({ verbose: true });
		console.log(moveHistory);
	});
</script>

<CustomCG bind:chessground bind:chess bind:flipBoard bind:piece bind:board {config} />
