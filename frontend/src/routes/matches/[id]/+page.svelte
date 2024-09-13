<script lang="ts">
	import Account from '$lib/components/Account2.svelte';
	import type { PageData } from './$types';
	import AnalysisCG from '$lib/components/AnalysisCG.svelte';
	import { onMount } from 'svelte';
	import { enhance } from '$app/forms';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { tick } from 'svelte';
	import type { ActionData } from './$types';

	export let data: PageData;
	export let form: ActionData;

	let engine: string = 'hyperfish';
	let depth: number = 5;
	let engineAnalysis: boolean = false;
	let highlights: string[] | undefined = undefined;

	const toastStore = getToastStore();

	let pos: number = data.match.moves.length;
	let set: (n: number) => void;
	let flipBoard: () => void;
	let loading = true;

	let flipped = false;
	function flip() {
		flipBoard();
		flipped = !flipped;
	}

	function first() {
		pos = 0;
		set(pos);
	}

	function back() {
		if (pos > 0) {
			pos = pos - 1;
			set(pos);
		}
	}

	function forward() {
		if (pos < data.match.moves.length) {
			pos = pos + 1;
			set(pos);
		}
	}

	function last() {
		pos = data.match.moves.length;
		set(pos);
	}

	function onMoveClick(movePos: number) {
		if (movePos <= data.match.moves.length) {
			pos = movePos;
			set(pos);
		}
	}

	onMount(async () => {
		loading = false;
	});
</script>

<div class="space-y-4">
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
		<div class="space-y-1">
			<div>
				<Account username={flipped ? data.match.white : data.match.black} {loading}></Account>
			</div>
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
			<div>
				<Account username={flipped ? data.match.black : data.match.white} {loading}></Account>
			</div>
		</div>

		<div>
			<div class="card p-5 gap-3">
				<h2 class="h2">Match analysis</h2>
				<!-- Moves -->
				<table>
					<tbody>
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
				<div>
					<button type="button" on:click={flip} class="btn-icon variant-filled">🔁</button>
					<button type="button" on:click={first} class="btn-icon variant-filled">⏪</button>
					<button type="button" on:click={back} class="btn-icon variant-filled">◀️</button>
					<button type="button" on:click={forward} class="btn-icon variant-filled">▶️</button>
					<button type="button" on:click={last} class="btn-icon variant-filled">⏩</button>
				</div>

				<form
					method="POST"
					use:enhance={() => {
						return async ({ update }) => {
							await update();
							await tick();

							if (form !== null) {
								console.log(form);
								highlights = form.map((move) => move.best);
								console.log(highlights);
							}
						};
					}}
				>
					<h2 class="h2">Engine Analysis</h2>
					<label class="label">
						<span>Select Engine</span>
						<select class="select" bind:value={engine} name="engine">
							{#each Object.entries(data.engines) as [i, name]}
								<option value={name}>{name}</option>
							{/each}
						</select>
					</label>
					<label class="label">
						<span>Engine depth: {depth}</span>
						<input
							type="range"
							min="1"
							max={engine == 'hyperfish' ? 8 : 20}
							bind:value={depth}
							name="depth"
						/>
					</label>
					<button type="submit" class="btn variant-ghost-primary self-start">Confirm</button>
				</form>
			</div>
		</div>
	</div>
</div>
