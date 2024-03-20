<script>
	import { tokenStore } from "$lib/stores";

	const loggedIn = $tokenStore !== "" && $tokenStore !== null;
	const updates = {
		"Announcement title": "announcement description",
	};
</script>

<div class="grid grid-cols-2 gap-4">
	<div>
		{#if !loggedIn}
			<h1 class="h1">Welcome to hyperchess</h1>
			<div class="py-4">
				<a
					href="/login"
					class="btn variant-ghost-primary"
					data-sveltekit-preload-data="hover">Log in</a
				>
				<a
					href="/register"
					class="btn variant-ghost-secondary"
					data-sveltekit-preload-data="hover">Sign up</a
				>
			</div>
		{:else}
			<h1 class="h1">Welcome username</h1>
		{/if}
	</div>
	<div>
		<h4 class="h4 end">Matches played today: XXXX</h4>
		<h4 class="h4 end">Ongoing games: XXXX</h4>
		<h4 class="h4 end">Active users: XXXX</h4>
	</div>
</div>

<h2 class="h2 py-4">Announcements</h2>
<div class="grid sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-4">
	{#each Object.entries(updates) as [title, desc]}
		<div class="block card card-hover p-4">
			<h4 class="h4">{title}</h4>
			<p>{desc}</p>
		</div>
	{/each}
</div>
