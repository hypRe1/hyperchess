<script lang="ts">
	import "../app.postcss";
	import {
		AppBar,
		AppShell,
		Avatar,
		Drawer,
		type DrawerSettings,
		Toast,
		popup,
		type PopupSettings,
		initializeStores,
		getDrawerStore,
	} from "@skeletonlabs/skeleton";
	import {
		computePosition,
		autoUpdate,
		offset,
		shift,
		flip,
		arrow,
	} from "@floating-ui/dom";

	import { storePopup } from "@skeletonlabs/skeleton";
	storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });

	const accountPopup: PopupSettings = {
		event: "click",
		target: "accountPopup",
		placement: "bottom",
	};

	const accountPopupLinks = {
		Account: "/account",
		Matches: "/matches",
	};

	import Navigation from "$lib/components/Navigation.svelte";
	import { tokenStore } from "$lib/stores";
	const loggedIn = $tokenStore !== "" && $tokenStore !== null;

	initializeStores();
	const drawerStore = getDrawerStore();

	const drawerSettings: DrawerSettings = {
		// Provide your property overrides:
		width: "w-[200px]",
		padding: "p-4",
		rounded: "rounded-xl",
	};

	function drawerOpen(): void {
		drawerStore.open(drawerSettings);
	}
</script>

<Drawer>
	<Navigation />
</Drawer>

<Toast position="br" />

<nav class="card p-4 list-nav" data-popup="accountPopup">
	<ul>
		{#each Object.entries(accountPopupLinks) as [title, url]}
			<li><a href={url}>{title}</a></li>
		{/each}
	</ul>
</nav>

<AppShell slotSidebarLeft="w-0 md:w-52 bg-surface-500/10">
	<svelte:fragment slot="header">
		<AppBar>
			<svelte:fragment slot="lead">
				<button class="md:hidden btn btn-sm mr-4" on:click={drawerOpen}>
					<span>
						<svg viewBox="0 0 100 80" class="fill-token w-4 h-4">
							<rect width="100" height="20" />
							<rect y="30" width="100" height="20" />
							<rect y="60" width="100" height="20" />
						</svg>
					</span>
				</button>
				<strong class="text-xl uppercase">hyperchess</strong>
			</svelte:fragment>
			<svelte:fragment slot="trail">
				{#if loggedIn}
					<div use:popup={accountPopup}>
						<Avatar
							src="http://127.0.0.1:8000/api/user/avatar"
							fallback="fallback_pfp.png"
							width="w-10"
							rounded="rounded-full"
						/>
					</div>
				{:else}
					<a
						href="/login"
						class="btn variant-ghost-primary"
						data-sveltekit-preload-data="hover">Log in</a
					>
				{/if}
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>
	<svelte:fragment slot="sidebarLeft">
		<Navigation />
	</svelte:fragment>
	<!-- <svelte:fragment slot="sidebarRight">Sidebar Right</svelte:fragment> -->
	<!-- <svelte:fragment slot="pageHeader">Page Header</svelte:fragment> -->
	<!-- Router Slot -->
	<div class="container p-10 mx-auto">
		<slot />
	</div>
	<!-- ---- / ---- -->
	<!-- <svelte:fragment slot="pageFooter">Page Footer</svelte:fragment> -->
	<!-- <svelte:fragment slot="footer">Footer</svelte:fragment> -->
</AppShell>
