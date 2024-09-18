<script lang="ts">
	import type { SvelteComponent } from 'svelte';

	import { getModalStore } from '@skeletonlabs/skeleton';

	// Props
	/** Exposes parent props to this component. */
	export let parent: SvelteComponent;

	const modalStore = getModalStore();

	// Form Data
	const formData = {
		password: '',
		confirm_password: ''
	};

	function onFormSubmit(): void {
		if (formData.password == formData.confirm_password) {
			if ($modalStore[0].response) $modalStore[0].response(formData.password);
			modalStore.close();
		}
	}

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const cForm = 'p-4 space-y-4 rounded-container-token';
</script>

<!-- @component Form modal for deleting user accounts. -->

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<header class={cHeader}>
			{$modalStore[0].title ?? '(title missing)'}
		</header>
		<!-- Enable for debugging: -->
		<form class="modal-form {cForm}">
			<label class="label">
				<span>Password</span>
				<input name="password" class="input" type="password" bind:value={formData.password} />
			</label>

			<label class="label">
				<span>Confirm Password</span>
				<input
					name="confirm password"
					class="input"
					type="password"
					bind:value={formData.confirm_password}
				/>
			</label>
		</form>
		<!-- prettier-ignore -->
		<footer class="modal-footer {parent.regionFooter}">
			<button class="btn {parent.buttonNeutral}" on:click={parent.onClose}>{parent.buttonTextCancel}</button>
			<button class="btn {parent.buttonPositive}" disabled={(formData.password != formData.confirm_password) || formData.password == ''} on:click={onFormSubmit}>Delete</button>
		</footer>
	</div>
{/if}
