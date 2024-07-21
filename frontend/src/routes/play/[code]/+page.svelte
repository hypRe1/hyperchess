<script lang="ts">
	import { Avatar } from '@skeletonlabs/skeleton';
	import { title } from '$lib/stores/title';
	import type { PageData } from './$types';
	import VsEngineCg from '$lib/components/vsEngineCG.svelte';

	export let data: PageData;

	title.set('Play vs hyperfish');

	let engine: string = 'hyperfish';
	let depth: number = 5;
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
		<div class="p-1 flex flex-row gap-2">
			<Avatar
				src="https://cdn-icons-png.flaticon.com/512/1250/1250593.png"
				width="w-12"
				rounded="rounded-full"
			/>
			<div>
				<h5 class="h5">{engine}</h5>
				<p>The powerful chess engine</p>
			</div>
		</div>
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

		<div class="p-2 flex flex-row gap-2">
			<Avatar src={data.avatar} width="w-12" rounded="rounded-full" />
			<div>
				<h5 class="h5">{data.username}</h5>
				<p>{data.about_me}</p>
			</div>
		</div>
	</div>
</div>
