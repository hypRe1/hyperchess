<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<svelte:head>
	<title>Hyperchess</title>
</svelte:head>

{#if !data.loggedIn}
	<h1 class="h1">Welcome to hyperchess</h1>
	<div class="py-4">
		<a href="/login" class="btn variant-ghost-primary">Log in</a>
		<a href="/register" class="btn variant-ghost-secondary">Sign up</a>
	</div>
{:else}
	<div class="flex flex-col space-y-4">
		<h1 class="h1">Welcome {data.profile?.username}</h1>
		<pre class="pre">To get started visit the demo.</pre>
		<a href="/demo" class="btn variant-ghost-primary self-start">Demo</a>
	</div>
{/if}
