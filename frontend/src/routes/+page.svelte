<script>
	import { tokenStore } from "$lib/stores";

	const loggedIn = $tokenStore !== "" && $tokenStore !== null;
</script>

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
	<h1 class="h1">You are logged in</h1>
{/if}
