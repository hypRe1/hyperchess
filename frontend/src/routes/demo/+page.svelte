<script lang="ts">
	import Account from '$lib/components/Account.svelte';
	import VsEngineCg from '$lib/components/vsEngineCG.svelte';
	import { title } from '$lib/stores/title';
	import type { PageData } from './$types';

	export let data: PageData;

	title.set('Play vs hyperfish');

	let engine: string = 'hyperfish';
	let depth: number = 5;

	let pieces: string[] = data.pieces;
	let boards: string[] = data.boards;

	let piece = data.piece;
	let board = data.board;
	let fen: string = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
	let undo: () => void;
	let flipBoard: () => void;
	let reset: () => void;
	let load_fen: (fen: string) => void;

	function engineChange() {
		if (depth > 8 && engine == 'hyperfish') {
			depth = 8;
		}
	}

	function fen_btn() {
		load_fen(fen);
	}
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
	<div>
		<div>
			<Account
				avatar="https://cdn-icons-png.flaticon.com/512/1250/1250593.png"
				bind:username={engine}
				admin={true}
				about_me="The powerful chess engine"
			></Account>
		</div>
		<div class="size-5/6">
			<VsEngineCg
				bind:depth
				bind:engine
				bind:piece
				bind:board
				bind:undo
				bind:flipBoard
				bind:reset
				bind:load_fen
			></VsEngineCg>
		</div>

		<div>
			<Account
				avatar={data.profile?.avatar}
				username={data.profile?.username}
				about_me={data.profile?.about_me}
				country={data.profile?.country}
				admin={data.profile?.admin}
			></Account>
		</div>
	</div>
	<div class="card p-5 gap-3">
		<h2 class="h2">Chess engine demo</h2>
		<div class="space-y-4 py-5">
			<label class="label">
				<span>Select Engine</span>
				<select class="select" bind:value={engine} on:change={engineChange} name="engineSelect">
					{#each Object.entries(data.engines) as [i, name]}
						<option value={name}>{name}</option>
					{/each}
				</select>
			</label>
			<label class="label">
				<span>Engine depth: {depth}</span>
				<input type="range" min="1" max={engine == 'hyperfish' ? 8 : 20} bind:value={depth} />
			</label>
			<button on:click={undo} type="button" class="btn variant-ghost self-start">Undo</button>
			<button on:click={flipBoard} type="button" class="btn variant-ghost self-start">Flip</button>
			<button on:click={reset} type="button" class="btn variant-ghost self-start">Reset</button>
			<label class="label">
				<span>Fen</span>
				<div class="space-y-2">
					<input class="textarea" name="fenInput" bind:value={fen} />
					<button on:click={fen_btn} type="button" class="btn variant-ghost self-start"
						>Load fen</button
					>
				</div>
			</label>
			<label class="label">
				<span>Piece</span>

				<select class="select" name="pieceInput" bind:value={piece}>
					{#each pieces as p}
						<option value={p}>{p}</option>
					{/each}
				</select>
			</label>

			<label class="label">
				<span>Board</span>

				<select class="select" name="boardInput" bind:value={board}>
					{#each boards as b}
						<option value={b}>{b}</option>
					{/each}
				</select>
			</label>
		</div>
	</div>
</div>
