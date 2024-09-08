<script lang="ts">
	import CustomCG from '$lib/components/CustomCG.svelte';
	import { Chessground } from 'svelte-chessground';

	export let piece: string;
	export let board: string;
	export let fen: string = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

	let chessground: Chessground;

	let config = {
		viewOnly: true,
		coordinates: false
	};
</script>

<CustomCG bind:chessground bind:piece bind:board {fen} {config} />
