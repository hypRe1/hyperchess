<script lang="ts">
	import { page } from "$app/stores";
</script>

<svelte:head>
	<title>Hyperchess</title>
</svelte:head>

{#if !$page.data.loggedIn}
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
	<div class="flex flex-col space-y-4">
		<h1 class="h1">Welcome {$page.data.username}</h1>
		<pre class="pre">To get started visit the demo.</pre>
		<a
			href="/demo"
			class="btn variant-ghost-primary self-start"
			data-sveltekit-preload-data="hover">Demo</a
		>
	</div>
{/if}
