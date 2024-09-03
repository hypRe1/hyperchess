<script lang="ts">
	import { goto } from '$app/navigation';
	import CreateMatchModal from '$lib/modals/createMatch.svelte';
	import FullScreenModal from '$lib/modals/fullScreen.svelte';
	import {
		addConnectionState,
		closeSocket,
		ConnectionState,
		connectSocket,
		sendMessage
	} from '$lib/stores/websocket';
	import type {
		MatchListing,
		MatchListingRequestForm
	} from '$lib/types/gameConnectionManagerTypes';
	import {
		getModalStore,
		getToastStore,
		type ModalComponent,
		type ModalSettings
	} from '@skeletonlabs/skeleton';
	import { onMount } from 'svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	const toastStore = getToastStore();
	const modalStore = getModalStore();

	let listings: MatchListing[] = [];
	let userListing: MatchListing | null = null;
	let invalidateSocket: boolean = true;

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
				toastStore.trigger({
					message: `Connected to websocket`,
					background: 'variant-filled-success',
					timeout: 5000
				});
				sendMessage(JSON.stringify(['listenListings']));
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
			case 'addListing':
				if (msgData.success) {
					userListing = msgData.listing;
					toastStore.trigger({
						message: `Created listing with code ${msgData.listing.code}`,
						background: 'variant-filled-success',
						timeout: 5000
					});
				} else {
					toastStore.trigger({
						message: msgData.detail,
						background: 'variant-filled-error',
						timeout: 5000
					});
				}
				break;
			case 'removeListing':
				if (msgData.success) {
					userListing = null;
					toastStore.trigger({
						message: `Deleted listing with code ${msgData.code}`,
						background: 'variant-filled-success',
						timeout: 5000
					});
				} else {
					toastStore.trigger({
						message: msgData.detail,
						background: 'variant-filled-error',
						timeout: 5000
					});
				}
				break;
			case 'listenListings':
				if (msgData.listings !== undefined) {
					listings = msgData.listings;
					addConnectionState(ConnectionState.LISTENING_LISTINGS);
				} else if (msgData.addListing !== undefined) {
					listings = [...listings, msgData.addListing];
				} else if (msgData.removeListing !== undefined) {
					listings = listings.filter((x) => {
						return x.code !== msgData.removeListing;
					});
				}
				break;

			case 'joinMatch':
				toastStore.trigger({
					message: 'Game started',
					background: 'variant-filled-success',
					timeout: 5000
				});
				invalidateSocket = false;
				addConnectionState(ConnectionState.MATCH_PLAYING);
				goto(`/play/${msgData}`);
		}
	};

	onMount(() => {
		connectSocket(handleMessage);

		return () => {
			sendMessage(JSON.stringify(['stopListenListings']));
			if (invalidateSocket) {
				closeSocket();
				toastStore.trigger({
					message: `Disconnected from websocket`,
					background: 'variant-filled-success',
					timeout: 2000
				});
			}
		};
	});
	function createListing(listingForm: MatchListingRequestForm) {
		sendMessage(JSON.stringify(['addListing', listingForm]));
	}

	function createListingBtn() {
		const c: ModalComponent = { ref: CreateMatchModal };
		const modal: ModalSettings = {
			type: 'component',
			component: c,
			title: 'Create Match',
			response: (r) => (typeof r !== 'undefined' && r !== false ? createListing(r) : null)
		};
		modalStore.trigger(modal);
	}

	function deleteListingBtn() {
		sendMessage(JSON.stringify(['removeListing']));
	}

	function getColourString(colour: boolean | null): string {
		if (colour === null) {
			return 'random';
		} else if (colour) {
			return 'white';
		} else {
			return 'black';
		}
	}

	function acceptListing(code: string) {
		sendMessage(JSON.stringify(['acceptListing', code]));
	}

	function fractionTime(time: number) {
		if (time == 0.5) {
			return '½';
		} else if (time == 0.25) {
			return '¼';
		} else {
			return time;
		}
	}
</script>

<h2 class="h2">Play chess</h2>
<button on:click={createListingBtn} type="button" class="btn variant-filled-primary"
	>Create Match</button
>
<button on:click={deleteListingBtn} type="button" class="btn variant-filled-primary"
	>Delete Match</button
>

<!-- Listings table -->
<div class="table-container">
	<table class="table table-interactive">
		<thead>
			<tr>
				<th>Code</th>
				<th>Colour</th>
				<th>Player</th>
				<th>Rating</th>
				<th>Time</th>
				<th>Mode</th>
			</tr>
		</thead>
		<tbody>
			{#if userListing !== null}
				<tr class="variant-ghost-secondary">
					<td><span class="badge variant-soft-primary">{userListing.code}</span></td>
					<td>{getColourString(userListing.colour)}</td>
					<td>{userListing.creator}</td>
					<td>blank</td>
					<td>{fractionTime(userListing.time)}+{userListing.bonus}</td>
					<td>blank</td>
				</tr>
			{/if}

			{#each listings as listing}
				{#if userListing == null || listing.code !== userListing.code}
					<tr on:click={() => acceptListing(listing.code)}>
						<td><span class="badge variant-soft-primary">{listing.code}</span></td>
						<td>{getColourString(listing.colour)}</td>
						<td>{listing.creator}</td>
						<td>blank</td>
						<td>{fractionTime(listing.time)}+{listing.bonus}</td>
						<td>blank</td>
					</tr>
				{/if}
			{/each}
		</tbody>
	</table>
</div>
