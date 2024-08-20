<script lang="ts">
	import Account from '$lib/components/Account.svelte';
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
	import { getToastStore, getModalStore, type ModalSettings, popup } from '@skeletonlabs/skeleton';
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
	let push_move: (
		move:
			| string
			| {
					from: string;
					to: string;
					promotion?: string;
			  }
	) => void;

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
				console.log(match);
				if (data.profile!.username == match.white_player) {
					boardMode = BoardMode.white;
				} else if (data.profile!.username == match.black_player) {
					boardMode = BoardMode.black;
				}
				for (var i = 0; i < match.moves.length; i++) push_move(match.moves[i]);
				toastStore.trigger({
					message: 'Joined match',
					background: 'variant-filled-success',
					timeout: 2000
				});
				break;
			case 'makeMove':
				if (msgData.success) {
					toastStore.trigger({
						message: 'Made move successfully',
						background: 'variant-filled-success',
						timeout: 2000
					});
				} else {
					toastStore.trigger({
						message: 'Failed to make move',
						background: 'variant-filled-error',
						timeout: 2000
					});
				}
				break;
			case 'pushMove':
				push_move(msgData);
				break;
		}
	};

	onMount(() => {
		connectSocket(handleMessage);
		if (hasConnectionState(ConnectionState.MATCH_PLAYING))
			sendMessage(JSON.stringify(['joinMatch', data.code]));

		return () => {
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
	<div>
		<div class="p-1 flex flex-row gap-2">
			<Account
				avatar={undefined}
				username={loading ? 'Black player' : match.black_player}
				about_me="Black player bio"
			></Account>
		</div>

		<VsPlayerCg bind:piece bind:board bind:flipBoard bind:push_move bind:mode={boardMode}
		></VsPlayerCg>

		<div>
			<Account
				avatar={undefined}
				username={loading ? 'White player' : match.white_player}
				about_me="White player bio"
			></Account>
		</div>
	</div>
	<div class="card p-5 gap-3">
		<h2 class="h2">Chess Match</h2>
	</div>
</div>
