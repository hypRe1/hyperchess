<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { title } from '$lib/stores/title';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { tick } from 'svelte';
	import type { ActionData } from './$types';

	// Set the page title
	title.set('Login');

	// Initialise the toast store for notifications
	const toastStore = getToastStore();

	export let form: ActionData;
</script>

<!-- Login form using SvelteKit form enhancement to handle form submissions -->
<form
	method="POST"
	use:enhance={() => {
		return async ({ update }) => {
			// Perform form submission and wait for update completion
			await update();
			await tick();

			// If the login failed trigger an error toast notification
			if (form?.detail != null && form?.error) {
				toastStore.trigger({
					message: form?.detail,
					background: 'variant-filled-error',
					timeout: 2000
				});
			}

			// If the login was successful trigger a success toast notification
			// and navigate to the home page
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

	<!-- Username input field -->
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

	<!-- Password input field -->
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

	<!-- Submit button -->
	<button type="submit" class="btn variant-ghost-primary self-start">Confirm</button>

	<!-- Link to register page -->
	<h3 class="h5">Or if you do not have an account</h3>
	<a
		href="/register"
		class="btn variant-ghost-secondary self-start"
		data-sveltekit-preload-data="hover">Sign up</a
	>
</form>
