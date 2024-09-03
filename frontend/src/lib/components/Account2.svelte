<script lang="ts">
	import Account from '$lib/components/Account.svelte';
	import { getProfile } from '$lib/util';

	export let username: string;
	export let loading: boolean;
</script>

{#if loading}
	<Account {username} avatar={undefined}></Account>
{:else}
	{#await getProfile(username)}
		<Account {username} avatar={undefined}></Account>
	{:then profile}
		<Account
			{username}
			avatar={profile.avatar}
			admin={profile.admin}
			country={profile.country}
			about_me={profile.about_me}
		></Account>
	{/await}
{/if}
