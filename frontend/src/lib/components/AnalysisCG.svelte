<script lang="ts">
	import CustomCG from '$lib/components/CustomCG.svelte';
	import { Chess } from 'chess.js';
	import { onMount } from 'svelte';
	import { Chessground } from 'svelte-chessground';

	export let piece: string;
	export let board: string;

	export let moves: string[];

	let positions: string[];
	export let flipBoard: () => void;

	export function set(pos: number) {
		if (assigned) {
			chessground.set({ fen: positions[pos] });
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
		}
		assigned = true;
	});
</script>

<CustomCG bind:chessground bind:chess bind:flipBoard bind:piece bind:board {config} />
