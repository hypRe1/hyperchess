<script lang="ts">
	import { Chessground } from 'svelte-chessground';
	import CustomCG from '$lib/components/CustomCG.svelte';
	import { Chess } from 'chess.js';
	import { onMount } from 'svelte';
	import { legalMoves, makePlayerMove } from '$lib/util';

	export let piece: string;
	export let board: string;

	export let flipBoard: () => void;

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
				movable: {
					events: {
						after: makePlayerMove(chessground, chess)
					}
				}
			});
		}
	}
</script>

<CustomCG bind:chessground bind:chess bind:flipBoard bind:piece bind:board {config} />
