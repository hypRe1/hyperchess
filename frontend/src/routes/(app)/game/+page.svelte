<script lang="ts">
	import { Chessground } from 'svelte-chessground';
	import { Chess } from 'chess.js';
	import { onMount } from 'svelte';
	import { toDests, playOtherSide } from '$lib/util.js';

	const chess = new Chess();

	let chessground: Chessground;

	let config = {
		movable: {
			color: 'white',
			free: false,
			dests: toDests(chess)
		}
	};

	onMount(async () => {
		chessground.set({
			movable: { events: { after: playOtherSide(chessground, chess) } }
		});
	});
</script>

<div class="grid grid-cols-2 gap-3">
	<div style="max-width:512px;">
		<Chessground bind:this={chessground} {config} />
	</div>

	<div>
		<h2 class="h2">Game</h2>
		<div class="py-2">
			<h6 class="h6">Its move 0, with white to play</h6>
			<p>Moves played:</p>
		</div>
	</div>
</div>
