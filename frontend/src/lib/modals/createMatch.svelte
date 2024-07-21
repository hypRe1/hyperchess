<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import type { MatchListingRequestForm } from '$lib/types/gameConnectionManagerTypes';

	// Stores
	import { getModalStore } from '@skeletonlabs/skeleton';

	// Props
	/** Exposes parent props to this component. */
	export let parent: SvelteComponent;

	const modalStore = getModalStore();

	// Form Data
	const formData: MatchListingRequestForm = {
		public: true,
		colour: null,
		time: 5,
		bonus: 3
	};

	let rawTime: number = 9;
	let rawBonus: number = 3;

	function convertRawTime(x: number): number {
		if (x < 5) return x / 4;
		else if (x < 7) return x / 2 - 1;
		else if (x < 25) return x - 4;
		else if (x < 30) return 5 * x - 100;
		else return 15 * x - 390;
	}

	function convertRawBonus(x: number): number {
		if (x < 21) return x;
		else if (x < 26) return 5 * x - 80;
		else if (x < 27) return 15 * x - 330;
		else return 30 * x - 720;
	}

	function updateTime() {
		formData.time = convertRawTime(rawTime);
	}

	function updateBonus() {
		formData.bonus = convertRawBonus(rawBonus);
	}

	// We've created a custom submit function to pass the response and close the modal.
	function onFormSubmit(): void {
		if ($modalStore[0].response) $modalStore[0].response(formData);
		modalStore.close();
	}

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const cForm = 'p-4 space-y-4 rounded-container-token';
</script>

<!-- @component This example creates a simple form modal. -->

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<header class={cHeader}>
			{$modalStore[0].title ?? '(title missing)'}
		</header>
		<!-- Enable for debugging: -->
		<form class="modal-form {cForm}">
			<label class="label">
				<span>Match visibility</span>

				<select
					name="visibility"
					class="select overflow-y-hidden"
					size="2"
					bind:value={formData.public}
				>
					<option value={true}>Public</option>
					<option value={false}>Private</option>
				</select>
			</label>
			<label class="label">
				<span>Colour</span>

				<select
					name="colour"
					class="select overflow-y-hidden"
					size="3"
					bind:value={formData.colour}
				>
					<option value={null}>Random</option>
					<option value={true}>White</option>
					<option value={false}>Black</option>
				</select>
			</label>
			<label class="label">
				<span>Minutes per side: {formData.time}</span>
				<input bind:value={rawTime} on:input={updateTime} type="range" min="0" max="38" />
			</label>
			<label class="label">
				<span>Increment in seconds: {formData.bonus}</span>
				<input
					class="variant-form-material"
					bind:value={rawBonus}
					on:input={updateBonus}
					type="range"
					min="0"
					max="30"
				/>
			</label>
		</form>
		<!-- prettier-ignore -->
		<footer class="modal-footer {parent.regionFooter}">
			<button class="btn {parent.buttonNeutral}" on:click={parent.onClose}>{parent.buttonTextCancel}</button>
			<button class="btn {parent.buttonPositive}" on:click={onFormSubmit}>Create</button>
		</footer>
	</div>
{/if}
