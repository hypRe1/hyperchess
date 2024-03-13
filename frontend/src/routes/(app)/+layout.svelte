<script lang="ts">
	import '../../app.postcss';
	import {
		AppShell,
		Avatar,
		AppRail,
		AppBar,
		AppRailAnchor,
		initializeStores,
		Modal,
		getModalStore
	} from '@skeletonlabs/skeleton';
	import type { ModalSettings, ModalComponent, ModalStore } from '@skeletonlabs/skeleton';
	initializeStores();
</script>

<Modal />

<!-- App Shell -->
<AppShell>
	<svelte:fragment slot="header">
		<!-- App Bar -->
		<AppBar>
			<svelte:fragment slot="lead">
				<a href="/">
					<strong class="text-xl">hyperchess</strong>
				</a>
			</svelte:fragment>
			<svelte:fragment slot="trail">
				<span>hypRe</span>
				<a href="/account">
					<Avatar
						border="border-2 border-surface-300-600-token hover:!border-primary-500"
						src="http://127.0.0.1:8000/api/user/avatar/hypre"
						width="w-12"
						rounded="rounded-full"
					/>
				</a>
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>
	<svelte:fragment slot="sidebarLeft">
		<!-- Sidebar left -->
		<AppRail>
			<!-- --- -->
			<a href="/home">
				<AppRailAnchor target="_blank" title="Home">
					<span>Home</span>
				</AppRailAnchor>
			</a>
			<a href="/play">
				<AppRailAnchor target="_blank" title="Play">
					<span>Play</span>
				</AppRailAnchor>
			</a>
			<a href="/train">
				<AppRailAnchor target="_blank" title="Train">
					<span>Train</span>
				</AppRailAnchor>
			</a>
			<a href="/insights">
				<AppRailAnchor target="_blank" title="Insights">
					<span>Insights</span>
				</AppRailAnchor>
			</a>

			<!-- --- -->
			<svelte:fragment slot="trail">
				<a href="/settings">
					<AppRailAnchor target="_blank" title="Settings">
						<div class="flex items-center justify-center">
							<img class="text-white" src="/settings.svg" alt="settings" />
						</div>
					</AppRailAnchor>
				</a>
			</svelte:fragment>
		</AppRail>
	</svelte:fragment>

	<div class="p-8">
		<slot />
	</div>
</AppShell>
