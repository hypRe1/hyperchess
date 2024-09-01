<script lang="ts">
	import type { SvelteComponent } from 'svelte';

	// Stores
	import { getModalStore } from '@skeletonlabs/skeleton';

	// Props
	/** Exposes parent props to this component. */
	export let parent: SvelteComponent;

	const modalStore = getModalStore();

	function onFormSubmit(accepted: Boolean, disabled: Boolean): void {
		if ($modalStore[0].response) $modalStore[0].response([accepted, disabled]);
		modalStore.close();
	}

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
</script>

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<header class={cHeader}>
			{$modalStore[0].title ?? '(title missing)'}
		</header>

		<!-- prettier-ignore -->
		<footer class="modal-footer {parent.regionFooter}">
            <button class="btn {parent.buttonNeutral}" on:click={() => onFormSubmit(false, true)}>Disable offers</button>
			<button class="btn {parent.buttonNeutral}" on:click={() => onFormSubmit(false, false)}>{parent.buttonTextCancel}</button>
			<button class="btn {parent.buttonPositive}" on:click={() => onFormSubmit(true, false)}>Confirm</button>
		</footer>
	</div>
{/if}
