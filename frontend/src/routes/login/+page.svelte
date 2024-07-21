<script lang="ts">
	import { enhance } from '$app/forms';
	import { tick } from 'svelte';
	import { goto } from '$app/navigation';
	import type { ActionData } from './$types';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { title } from '$lib/stores/title';

	title.set('Login');

	const toastStore = getToastStore();
	export let form: ActionData;
</script>

<form
	method="POST"
	use:enhance={() => {
		return async ({ update }) => {
			await update();
			await tick();
			if (form?.detail != null && form?.error) {
				toastStore.trigger({
					message: form?.detail,
					background: 'variant-filled-error',
					timeout: 2000
				});
			}

			if (form?.success) {
				toastStore.trigger({
					message: 'Logged in successfully!',
					background: 'variant-filled-success',
					timeout: 2000
				});
				await goto('/', {
					replaceState: true,
					invalidateAll: true
				});
			}
		};
	}}
	class="card p-4 flex flex-col gap-3 container h-full mx-auto"
>
	<h2 class="h2">Login</h2>
	<input
		class="input"
		name="username"
		title="Input (username)"
		type="text"
		placeholder="Username"
		autocomplete="username"
		required
		minlength="3"
		maxlength="32"
	/>
	<input
		class="input"
		name="password"
		title="Input (password)"
		type="password"
		placeholder="Password"
		autocomplete="current-password"
		required
		minlength="6"
		maxlength="125"
	/>
	<button type="submit" class="btn variant-ghost-primary self-start">Confirm</button>
	<h3 class="h5">Or if you do not have an account</h3>
	<a
		href="/register"
		class="btn variant-ghost-secondary self-start"
		data-sveltekit-preload-data="hover">Sign up</a
	>
</form>
