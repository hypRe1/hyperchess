<script lang="ts">
	import type { PageData } from './$types';
	import PreviewCg from '$lib/components/previewCG.svelte';

	export let data: PageData;
</script>

<div class="space-y-4">
	<h2 class="h2">Archived matches 📁</h2>

	{#each data.matches as match}
		<a class="card card-hover flex flex-row items-center gap-4 p-2" href="/matches/{match.id}">
			<div class="size-32">
				<PreviewCg piece={data.appearance.piece} board={data.appearance.board} fen={match.fen}
				></PreviewCg>
			</div>
			<p>{match.time}+{match.bonus}</p>
			<div></div>
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

			<p>{match.n_moves} moves</p>
			<p class="code">{match.time_started}</p>
		</a>
	{/each}
</div>
