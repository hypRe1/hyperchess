<script lang="ts">
	import CustomCG from '$lib/components/CustomCG.svelte';
	import { Chessground } from 'svelte-chessground';
	export let piece: string;
	export let board: string;

	let chessground: Chessground;

	let config = {
		viewOnly: true,
		coordinates: false
	};
</script>

<CustomCG bind:chessground bind:piece bind:board {config} />
