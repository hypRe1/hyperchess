<script lang="ts">
	import { enhance } from '$app/forms';
	import Account from '$lib/components/Account2.svelte';
	import AnalysisCG from '$lib/components/AnalysisCG.svelte';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { onMount, tick } from 'svelte';
	import type { ActionData, PageData } from './$types';
	import { title } from '$lib/stores/title';
	import { ProgressBar } from '@skeletonlabs/skeleton';

	// Page data injected from server response
	export let data: PageData;
	// Engine analysis form results from server
	export let form: ActionData;

	// Set the page title
	title.set('Match analysis');

	// Initialise the toast store for notifications
	const toastStore = getToastStore();

	let engine: string = 'hyperfish'; // Default chess engine
	let depth: number = 5; // Default depth
	let engineAnalysis: boolean = false; // Whether engine analysis is active
	let highlights: string[] | undefined = undefined; // Highlights for moves, populate after analysis
	let scores: { per: number; label: number }[] | undefined = undefined;

	let pos: number = data.match.moves.length; // Track current position in game
	let set: (n: number) => void; // Function to set the current move position
	let flipBoard: () => void; // Function to flip the board
	let loading = true; // Loading state for account components

	// States to toggle visibility of moves and engine analysis section
	let movesHidden = false;
	let engineHidden = false;

	// Board flip state
	let flipped = false;

	function onMoveClick(movePos: number) {
		if (movePos <= data.match.moves.length) {
			pos = movePos;
			set(pos);
		}
	}

	function onKeyDown(e: KeyboardEvent) {
		switch (e.key) {
			case 'ArrowLeft':
				if (pos > 0) {
					pos = pos - 1;
					set(pos);
				}
				break;
			case 'ArrowRight':
				if (pos < data.match.moves.length) {
					pos = pos + 1;
					set(pos);
				}
				break;
		}
	}

	onMount(async () => {
		// Set loading to false once component is mounted to the DOM
		loading = false;
	});
</script>

<div class="space-y-4">
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
		<!-- Left column: Account details and chessboard -->
		<div class="space-y-1">
			<!-- Account component for opposite side player -->
			<div>
				<Account username={flipped ? data.match.white : data.match.black} {loading}></Account>
			</div>

			<!-- Chessboard component -->
			<div class="size-5/6">
				<AnalysisCG
					piece={data.appearance.piece}
					board={data.appearance.board}
					moves={data.match.moves}
					bind:highlights
					bind:set
					bind:flipBoard
				></AnalysisCG>
			</div>

			<!-- Account component for same side player -->
			<div>
				<Account username={flipped ? data.match.black : data.match.white} {loading}></Account>
			</div>
		</div>

		<!-- Right column: Match moves and engine analysis -->
		<div>
			<div class="card p-5 gap-3">
				<h2 class="h2">Match analysis</h2>
				<!-- Section collapser buttons -->
				<button on:click={() => (movesHidden = !movesHidden)}>
					<button type="button" class="btn btn-sm variant-filled"
						>{movesHidden ? 'Show' : 'Hide'} Moves</button
					>
				</button>

				<button on:click={() => (engineHidden = !engineHidden)}>
					<button type="button" class="btn btn-sm variant-filled"
						>{engineHidden ? 'Show' : 'Hide'} Engine Analysis</button
					>
				</button>

				<button on:click={() => (engineHidden = !engineHidden)}>
					<button type="button" class="btn btn-sm variant-filled"
						>{engineHidden ? 'Show' : 'Hide'} Principal Variation</button
					>
				</button>

				<!-- Moves section -->
				<div hidden={movesHidden}>
					<table>
						<tbody>
							<!-- Loop through the first half of the moves, displaying two moves per row -->
							{#each data.match.moves.slice(0, Math.ceil(data.match.moves.length / 2)) as _, index}
								<tr>
									<td>{index + 1}.</td>
									<td
										on:click={() => onMoveClick(index * 2 + 1)}
										class={index * 2 + 1 == pos ? 'bg-primary-500' : ''}
										><span>{data.match.moves[index * 2]}</span></td
									>
									<td
										on:click={() => onMoveClick(index * 2 + 2)}
										class={index * 2 + 2 == pos ? 'bg-primary-500' : ''}
										>{data.match.moves[index * 2 + 1] || ''}</td
									>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Engine analysis section -->
				<div hidden={engineHidden} class="space-y-1">
					<form
						method="POST"
						use:enhance={() => {
							return async ({ update }) => {
								await update();
								await tick();

								engineAnalysis = true;

								toastStore.trigger({
									message: `Finished engine analysis`,
									background: 'variant-filled-success',
									timeout: 4000
								});

								if (form !== null) {
									// @ts-ignore
									highlights = form.map((move) => move.best);
									// @ts-ignore
									scores = form.map((move) => move.score);
									console.log(highlights);
								}
							};
						}}
					>
						<h3 class="h3">Engine Analysis</h3>

						<!-- Engine selection dropdown -->
						<label class="label">
							<span>Select Engine</span>
							<select class="select" bind:value={engine} name="engine">
								{#each Object.entries(data.engines) as [i, name]}
									<option value={name}>{name}</option>
								{/each}
							</select>
						</label>

						<!-- Engine depth slider -->
						<label class="label">
							<span>Engine depth: {depth}</span>
							<input type="range" min="1" max="19" bind:value={depth} name="depth" />
						</label>

						<!-- Submit button for engine analysis form -->
						<button type="submit" class="btn variant-ghost-primary self-start">Confirm</button>
					</form>
				</div>

				<!-- Navigation buttons for chess moves and board flip -->
				<div>
					<button
						type="button"
						on:click={() => {
							flipBoard();
							flipped = !flipped;
						}}
						class="btn-icon variant-filled">🔁</button
					>
					<button
						type="button"
						on:click={() => {
							pos = 0;
							set(pos);
						}}
						class="btn-icon variant-filled">⏪</button
					>
					<button
						type="button"
						on:click={() => {
							if (pos > 0) {
								pos = pos - 1;
								set(pos);
							}
						}}
						class="btn-icon variant-filled">◀️</button
					>
					<button
						type="button"
						on:click={() => {
							if (pos < data.match.moves.length) {
								pos = pos + 1;
								set(pos);
							}
						}}
						class="btn-icon variant-filled">▶️</button
					>
					<button
						type="button"
						on:click={() => {
							pos = data.match.moves.length;
							set(pos);
						}}
						class="btn-icon variant-filled">⏩</button
					>
				</div>
			</div>
			{#if scores}
				<div class="p-4">
					<strong>{scores[pos].label}</strong>
					<ProgressBar value={scores[pos].per} min={0} max={100} height="h-10" />
				</div>
			{/if}
		</div>
	</div>
</div>

<svelte:window on:keydown={onKeyDown} />
