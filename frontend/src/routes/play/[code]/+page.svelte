<script lang="ts">
	import Account from '$lib/components/Account2.svelte';
	import { title } from '$lib/stores/title';
	import type { PageData } from './$types';
	import {
		ConnectionState,
		connectSocket,
		closeSocket,
		sendMessage,
		hasConnectionState
	} from '$lib/stores/websocket';
	import { onMount } from 'svelte';
	import { getToastStore, getModalStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import FullScreenModal from '$lib/modals/fullScreen.svelte';
	import VsPlayerCg from '$lib/components/vsPlayerCG.svelte';
	import type { MatchModel } from '$lib/types/matchModelsTypes';
	export let data: PageData;

	title.set(`Match [${data.code}]`);

	const toastStore = getToastStore();
	const modalStore = getModalStore();

	let loading = true;
	let piece = data.piece;
	let board = data.board;
	let match: MatchModel;
	enum BoardMode {
		white,
		black,
		spectate
	}
	let boardMode = BoardMode.spectate;

	let flipBoard: () => void;
	let history: () => string[];
	let turn: () => boolean;
	let push_move: (
		move:
			| string
			| {
					from: string;
					to: string;
					promotion?: string;
			  }
	) => void;

	const results = [
		'ongoing',
		'checkmate',
		'resign',
		'flagged',
		'stalemate',
		'insufficient material',
		'repetition',
		'75 move rule'
	];

	let moves: string[] = [];
	let result: string = '';
	let bt: number = 0;
	let wt: number = 0;

	let timerInterval: NodeJS.Timeout;

	function displayTime(seconds: number): string {
		return `${Math.floor(seconds / 60)
			.toString()
			.padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
	}

	const handleMessage = (event: MessageEvent) => {
		const msg = JSON.parse(event.data);
		let cmd = msg[0];
		let msgData = msg[1];

		switch (cmd) {
			case 'tokenRequest':
				if (data.token !== undefined) {
					sendMessage(data.token);
				}
				break;
			case 'connected':
				sendMessage(JSON.stringify(['joinMatch', data.code]));
				break;
			case 'disconnected':
				const modal: ModalSettings = {
					type: 'component',
					component: { ref: FullScreenModal },
					title: 'Disconnected',
					body: msgData['details'],
					backdropClasses: '!p-0'
				};
				modalStore.trigger(modal);
				break;
			case 'joinMatch':
				loading = false;
				match = msgData;

				wt = bt = match.time * 60;
				function updateTimer() {
					if (!match.game_over) {
						let _turn: boolean = turn();
						let d = new Date();
						let seconds = Math.round(d.getTime() / 1000);
						let time_spent =
							seconds - match.time_created! - match.timings!.reduce((a, b) => a + b, 0);
						let time_left =
							match.time * 60 -
							time_spent -
							match
								.timings!.slice(+!_turn)
								.filter((_, i) => i % 2 === 0)
								.reduce((acc, timing) => acc + (timing - match.bonus), 0);

						if (time_left >= 0) _turn ? (wt = Math.round(time_left)) : (bt = Math.round(time_left));
						if (time_left <= 0) sendMessage(JSON.stringify(['checkClock']));
					} else {
						clearInterval(timerInterval);
					}
				}

				timerInterval = setInterval(updateTimer, 100);

				if (data.profile!.username == match.white_player) {
					boardMode = BoardMode.white;
				} else if (data.profile!.username == match.black_player) {
					boardMode = BoardMode.black;
				}
				for (var i = 0; i < match.moves.length; i++) push_move(match.moves[i]);
				moves = history();
				toastStore.trigger({
					message: 'Joined match',
					background: 'variant-filled-success',
					timeout: 2000
				});
				break;
			case 'makeMove':
				if (msgData.success) {
					turn() ? (bt = bt + match.bonus) : (wt = wt + match.bonus);
					match.timings?.push(msgData.time);
					moves = history();
				} else {
					toastStore.trigger({
						message: 'Failed to make move',
						background: 'variant-filled-error',
						timeout: 2000
					});
				}
				break;
			case 'pushMove':
				turn() ? (wt = wt + match.bonus) : (bt = bt + match.bonus);
				match.timings?.push(msgData.time);
				push_move(msgData.move);
				moves = history();
				break;
			case 'gameOver':
				boardMode = BoardMode.spectate;
				match.game_over = true;
				match.result = msgData.result;
				match.winner = msgData.winner;
				result = results[msgData.result];
				toastStore.trigger({
					message: `Game over`,
					background: 'variant-filled-success',
					timeout: 2000
				});
				break;
		}
	};

	onMount(() => {
		connectSocket(handleMessage);
		if (hasConnectionState(ConnectionState.MATCH_PLAYING))
			sendMessage(JSON.stringify(['joinMatch', data.code]));

		return () => {
			clearInterval(timerInterval);
			closeSocket();
			toastStore.trigger({
				message: `Disconnected from websocket`,
				background: 'variant-filled-success',
				timeout: 2000
			});
		};
	});
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
	<div class="space-y-1">
		<div class="columns-3">
			{#if boardMode !== BoardMode.black}
				<Account username={loading ? 'Black player' : match.black_player} {loading}></Account>
				<h2 class="h2 text-center">{displayTime(bt)}</h2>
				<span>Captured pieces</span>
			{:else}
				<Account username={loading ? 'White player' : match.white_player} {loading}></Account>
				<h2 class="h2 text-center">{displayTime(wt)}</h2>
				<span>Captured pieces</span>
			{/if}
		</div>

		<div>
			<VsPlayerCg
				bind:history
				bind:turn
				bind:piece
				bind:board
				bind:flipBoard
				bind:push_move
				bind:mode={boardMode}
			></VsPlayerCg>
		</div>

		<div class="columns-3">
			{#if boardMode === BoardMode.black}
				<Account username={loading ? 'Black player' : match.black_player} {loading}></Account>
				<h2 class="h2 text-center">{displayTime(bt)}</h2>
				<span>Captured pieces</span>
			{:else}
				<Account username={loading ? 'White player' : match.white_player} {loading}></Account>
				<h2 class="h2 text-center">{displayTime(wt)}</h2>
				<span>Captured pieces</span>
			{/if}
		</div>
	</div>
	<div class="p-5 gap-3 overflow-y-scroll bg-surface-500/25">
		<h2 class="h2">Chess Match</h2>

		<div>
			<table>
				<tbody>
					{#each moves.slice(0, Math.ceil(moves.length / 2)) as _, index}
						<tr>
							<td>{index + 1}.</td>
							<td>{moves[index * 2]}</td>
							<td>{moves[index * 2 + 1] || ''}</td>
						</tr>
					{/each}
				</tbody>
			</table>
			{#if match && match.game_over}
				<span>Game over: {result}</span>
				<br />
				{#if match.winner === null}
					<span>½-½</span>
				{:else if match.winner}
					<span>{match.white_player} wins!</span>
					<br />
					<span>1-0</span>
				{:else}
					<span>{match.black_player} wins!</span>
					<br />
					<span>0-1</span>
				{/if}
			{/if}
		</div>
	</div>
</div>

<style>
	table {
		border-collapse: collapse; /* Ensures that spacing is controlled by padding */
		width: 100%; /* Makes the table take up the full width of the container */
	}

	td {
		border-bottom: 1px solid #ddd; /* Optional: Adds a border between rows */
	}

	td:first-child {
		width: 8%; /* Adjust the percentage as needed */
		white-space: nowrap; /* Prevents the number from wrapping */
	}

	td:nth-child(2) {
		width: 16%; /* Adjust the percentage as needed */
		white-space: nowrap; /* Prevents the number from wrapping */
	}
</style>
