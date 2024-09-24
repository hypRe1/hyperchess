<script lang="ts">
	import PreviewCg from '$lib/components/previewCG.svelte';
	import type { PageData } from './$types';
	import { title } from '$lib/stores/title';

	// Page data injected from server response
	export let data: PageData;

	// Set the page title
	title.set('Matches');
</script>

<div class="space-y-4">
	<h2 class="h2">Archived matches 📁</h2>

	{#if data.matches.length == 0}
		<h3 class="h3">Play a match or add a match in PGN notation</h3>
	{/if}

	<!-- Loop through matches displaying each one -->
	{#each data.matches as match}
		<!-- Link to match analysis page -->
		<a class="card card-hover flex flex-row items-center gap-4 p-2" href="/matches/{match.id}">
			<!-- Game preview -->
			<div class="size-32">
				<PreviewCg piece={data.appearance.piece} board={data.appearance.board} fen={match.fen}
				></PreviewCg>
			</div>
			<!--Match time and bonus -->
			<p>{match.time}+{match.bonus}</p>
			<!-- Match result -->
			<div>
				{#if match.winner === null}
					<p class="bg-yellow-50">½ {match.white}</p>
					<p class="bg-yellow-50">½ {match.black}</p>
				{:else if match.winner}
					<p class="bg-green-500">1 {match.white}</p>
					<p class="bg-red-500">0 {match.black}</p>
				{:else}
					<p class="bg-red-500">0 {match.white}</p>
					<p class="bg-green-500">1 {match.black}</p>
				{/if}
			</div>

			<!-- Number of (half) moves -->
			<p>{match.n_moves} moves</p>
			<!-- Time match started -->
			<p class="code">{match.time_started}</p>
		</a>
	{/each}
</div>
