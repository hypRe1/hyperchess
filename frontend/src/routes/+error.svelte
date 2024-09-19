<script lang="ts">
	import { page } from '$app/stores';
	import { title } from '$lib/stores/title';
	import { onMount } from 'svelte';

	title.set(`${$page.status} ${$page.error?.message}`);

	let gif: string | null = null;

	onMount(async () => {
		const resp = await fetch(
			`https://api.giphy.com/v1/gifs/random?api_key=0UTRbFtkMxAplrohufYco5IY74U8hOes&tag=cat&rating=g`,
			{
				method: 'GET'
			}
		);
		const respJson = await resp.json();
		gif = respJson.data.images.original.url;
	});
</script>

<h1 class="h1">{$page.status}: {$page.error?.message}</h1>
{#if gif}
	<img src={gif} alt="fail" />
{/if}
