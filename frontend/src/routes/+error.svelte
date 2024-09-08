<script>
	import { page } from '$app/stores';
	import { title } from '$lib/stores/title';

	title.set(`${$page.status} ${$page.error?.message}`);

	async function get_gif() {
		const resp = await fetch(
			`https://api.giphy.com/v1/gifs/random?api_key=0UTRbFtkMxAplrohufYco5IY74U8hOes&tag=error&rating=g`,
			{
				method: 'GET'
			}
		);
		const respJson = await resp.json();
		return respJson.data.images.original.url;
	}
</script>

<h1 class="h1">{$page.status}: {$page.error?.message}</h1>
{#await get_gif() then gif}
	<img src={gif} alt="fail" />
{/await}
