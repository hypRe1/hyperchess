<script lang="ts">
	import { Avatar } from '@skeletonlabs/skeleton';
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
	import {
		getToastStore,
		getModalStore,
		type ModalComponent,
		type ModalSettings
	} from '@skeletonlabs/skeleton';
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

	let fen: string = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
	let flipBoard: () => void;

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
				break;
		}
	};

	onMount(() => {
		connectSocket(handleMessage);

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

<div>
	<div class="p-1 flex flex-row gap-2">
		<Avatar width="w-12" rounded="rounded-full" />

		<div>
			<h5 class="h5">
				{loading ? 'Black player' : match.black_player}
			</h5>
			<p>Black player bio</p>
		</div>
	</div>

	<div style="width: 320; height: 320;">
		<VsPlayerCg bind:piece bind:board bind:flipBoard></VsPlayerCg>
	</div>

	<div class="p-2 flex flex-row gap-2">
		<Avatar
			class={loading ? 'placeholder animate-pulse' : ''}
			src={data.avatar}
			width="w-12"
			rounded="rounded-full"
		/>
		<div>
			<h5 class="h5">
				{loading ? 'White player' : match.white_player}
			</h5>
			<p>White player bio</p>
		</div>
	</div>
</div>
