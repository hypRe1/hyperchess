<script lang="ts">
	import { enhance } from '$app/forms';
	import { tick } from 'svelte';
	import { goto } from '$app/navigation';
	import type { ActionData } from './$types';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { title } from '$lib/stores/title';

	title.set('Sign up');

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
					message: 'Signed up successfully!',
					background: 'variant-filled-success',
					timeout: 2000
				});
				goto('/');
			}
		};
	}}
	class="card p-4 flex flex-col gap-3 container h-full mx-auto flex flex-col"
>
	<h2 class="h2">Sign up</h2>
	<input
		id="username"
		name="username"
		class="input"
		title="Input (username)"
		type="text"
		placeholder="Username"
		autocomplete="username"
		required
		minlength="3"
		maxlength="32"
	/>
	<input
		id="email"
		name="email"
		class="input"
		title="Input (email)"
		type="email"
		placeholder="Email"
		autocomplete="email"
		required
		maxlength="255"
	/>
	<input
		id="password"
		name="password"
		class="input"
		title="Input (password)"
		type="password"
		placeholder="Password"
		autocomplete="new-password"
		required
		minlength="6"
		maxlength="125"
	/>
	<input
		id="confirm_password"
		name="confirm password"
		class="input"
		title="Input (confirm password)"
		type="password"
		placeholder="Confirm Password"
		autocomplete="current-password"
		required
		minlength="6"
		maxlength="125"
	/>
	<button type="submit" class="btn variant-ghost-primary self-start">Confirm</button>
</form>
