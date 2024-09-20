<script lang="ts">
	import Account from '$lib/components/Account2.svelte';
	import VsPlayerCg from '$lib/components/vsPlayerCG.svelte';
	import DrawModal from '$lib/modals/draw.svelte';
	import FullScreenModal from '$lib/modals/fullScreen.svelte';
	import { title } from '$lib/stores/title';
	import {
		closeSocket,
		ConnectionState,
		connectSocket,
		hasConnectionState,
		sendMessage
	} from '$lib/stores/websocket';
	import type { MatchModel } from '$lib/types/matchModelsTypes';
	import { getModalStore, getToastStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import { error } from '@sveltejs/kit';
	import { onMount } from 'svelte';
	import type { PageData } from './$types';

	// Page data injected from the server response
	export let data: PageData;

	// Set the page title
	title.set(`Match [${data.code}]`);

	// Initialise toast and modal stores
	const toastStore = getToastStore();
	const modalStore = getModalStore();

	let loading = true; // Loading state for account components
	let match: MatchModel; // Stores the match details

	// Enumeration for different board modes
	enum BoardMode {
		white,
		black,
		spectate
	}
	let boardMode = BoardMode.spectate; // Default to spectate mode

	// Declare bound functions for chessboard component
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

	// Possible match results
	const results = [
		'ongoing',
		'checkmate',
		'resign',
		'flagged',
		'drawn by agreement',
		'stalemate',
		'insufficient material',
		'repetition',
		'75 move rule'
	];

	// Track moves, match result and timers for each player
	let moves: string[] = [];
	let result: string = '';
	let bt: number = 0; // Black player's time
	let wt: number = 0; // White player's time

	let timerInterval: NodeJS.Timeout; // Interval for updating the timers

	// Function to calculate both player's timers based on time spent on each move
	function updateTimers() {
		let _turn = turn();
		let d = new Date();
		let seconds = Math.round(d.getTime() / 1000);
		let time_spent = seconds - match.time_started! - match.timings!.reduce((a, b) => a + b, 0);
		let white_time_left =
			match.time * 60 +
			match.bonus -
			match
				.timings!.slice(0)
				.filter((_, i) => i % 2 === 0)
				.reduce((acc, timing) => acc + (timing - match.bonus), 0);
		let black_time_left =
			match.time * 60 +
			match.bonus -
			match
				.timings!.slice(1)
				.filter((_, i) => i % 2 === 0)
				.reduce((acc, timing) => acc + (timing - match.bonus), 0);

		_turn
			? (white_time_left = white_time_left - time_spent)
			: (black_time_left = black_time_left - time_spent);

		if (white_time_left < 0) white_time_left = 0;
		if (black_time_left < 0) black_time_left = 0;

		wt = Math.round(white_time_left);
		bt = Math.round(black_time_left);
	}

	// Function to display clock time
	function displayTime(seconds: number): string {
		if (seconds == 0) return '💀';
		if (seconds < 10) return `${seconds} ${seconds % 2 ? '😨' : '😰'}`;

		return `${Math.floor(seconds / 60)
			.toString()
			.padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
	}

	// Handle resign button click with confirmation modal
	function resignBtn() {
		function modalResp(r: boolean) {
			if (r) sendMessage(JSON.stringify(['resign']));
		}

		const modal: ModalSettings = {
			type: 'confirm',
			title: 'Resign',
			body: 'You will lose the match!',
			response: (r: boolean) => modalResp(r)
		};
		modalStore.trigger(modal);
	}

	// Handle draw button click with confirmation modal
	function drawBtn() {
		function modalResp(r: boolean) {
			if (r) sendMessage(JSON.stringify(['draw', 'offer']));
		}

		const modal: ModalSettings = {
			type: 'confirm',
			title: 'Draw',
			body: 'Are you sure you want to send a draw offer?',
			response: (r: boolean) => modalResp(r)
		};
		modalStore.trigger(modal);
	}

	// WebSocket message handler
	const handleMessage = (event: MessageEvent) => {
		const msg = JSON.parse(event.data);
		let cmd = msg[0];
		let msgData = msg[1];

		switch (cmd) {
			// When server requests token send back user token
			case 'tokenRequest':
				if (data.token !== undefined) {
					sendMessage(data.token);
				}
				break;

			// When first connected to websocket send join match request with match code
			case 'connected':
				sendMessage(JSON.stringify(['joinMatch', data.code]));
				break;

			// When disconnected from websocket trigger fullscreen disconnect modal
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

			// When user joins a match
			case 'joinMatch':
				if (msgData.success === false) {
					toastStore.trigger({
						message: msgData.detail,
						background: 'variant-filled-error',
						timeout: 2000
					});
					throw error(404);
				}

				loading = false; // Account components can now be loaded
				match = msgData;

				wt = bt = match.time * 60; // Initialise clock timer

				// Set board mode
				if (data.profile!.username == match.white_player) {
					boardMode = BoardMode.white;
				} else if (data.profile!.username == match.black_player) {
					boardMode = BoardMode.black;
				}

				// Push the existing moves
				for (var i = 0; i < match.moves.length; i++) push_move(match.moves[i]);
				moves = history();

				// Notify the user that they have successfully joined the match
				toastStore.trigger({
					message: 'Joined match',
					background: 'variant-filled-success',
					timeout: 2000
				});

				// Update both player's timers
				updateTimers();

				// Function to calculate the timer of the player whos turn it is
				function updateTimer() {
					if (!match.game_over) {
						let _turn: boolean = turn();
						let d = new Date();
						let seconds = Math.round(d.getTime() / 1000);
						let time_spent =
							seconds - match.time_started! - match.timings!.reduce((a, b) => a + b, 0);
						let time_left =
							match.time * 60 +
							match.bonus -
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

				// Calculate the timer of the player whos turn it is every 100ms
				timerInterval = setInterval(updateTimer, 100);
				break;

			// When user makes a move
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

			// When other player makes a move
			case 'pushMove':
				turn() ? (wt = wt + match.bonus) : (bt = bt + match.bonus);
				match.timings?.push(msgData.time);
				push_move(msgData.move);
				moves = history();
				break;

			// When game is over
			case 'gameOver':
				updateTimers();
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

			// When a draw is sent, offered, accepted or declined
			case 'draw':
				switch (msgData) {
					case 'offer':
						toastStore.trigger({
							message: 'Draw offer recieved',
							background: 'variant-filled-success',
							timeout: 2000
						});

						function modalResp(accepted: boolean, disabled: boolean) {
							accepted
								? sendMessage(JSON.stringify(['draw', 'accept']))
								: sendMessage(JSON.stringify(['draw', 'decline']));

							if (disabled) sendMessage(JSON.stringify(['draw', 'disable']));
						}

						const modal: ModalSettings = {
							type: 'component',
							component: { ref: DrawModal },
							title: 'Draw offer',
							response: (r) => modalResp(r[0], r[1])
						};
						modalStore.trigger(modal);
						break;
					case 'accept':
						toastStore.trigger({
							message: 'Draw offer accepted',
							background: 'variant-filled-success',
							timeout: 2000
						});
						break;
					case 'sent':
						toastStore.trigger({
							message: 'Draw offer sent',
							background: 'variant-filled-success',
							timeout: 2000
						});
						break;
					case 'decline':
						toastStore.trigger({
							message: 'Draw offer declined',
							background: 'variant-filled-error',
							timeout: 2000
						});
						break;
					case 'error':
						toastStore.trigger({
							message: msg[2],
							background: 'variant-filled-error',
							timeout: 2000
						});
						break;
				}
		}
	};

	onMount(() => {
		connectSocket(window.location.host, handleMessage);
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
		<!-- Player above board -->
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

		<!-- Board -->
		<div>
			<VsPlayerCg
				bind:history
				bind:turn
				piece={data.appearance.piece}
				board={data.appearance.board}
				bind:flipBoard
				bind:push_move
				bind:mode={boardMode}
			></VsPlayerCg>
		</div>

		<!-- Player below board -->
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

	<!-- Chess match menu -->
	<div class="p-5 gap-3 overflow-y-scroll bg-surface-500/25">
		<h2 class="h2">Chess Match</h2>
		<button
			on:click={resignBtn}
			disabled={loading || match.game_over}
			type="button"
			class="btn variant-filled-primary">Resign</button
		>
		<button
			on:click={drawBtn}
			disabled={loading || match.game_over}
			type="button"
			class="btn variant-filled-primary">Offer draw</button
		>

		<div>
			<!-- Moves -->
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

			<!-- Match result -->
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
		border-collapse: collapse;
		width: 100%;
	}

	td {
		border-bottom: 1px solid #ddd;
	}

	td:first-child {
		width: 8%;
		white-space: nowrap;
	}

	td:nth-child(2) {
		width: 16%;
		white-space: nowrap;
	}
</style>
