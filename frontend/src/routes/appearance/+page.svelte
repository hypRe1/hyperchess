<script lang="ts">
	import PreviewCg from '$lib/components/previewCG.svelte';
	import { title } from '$lib/stores/title';
	import type { Boards, Pieces, Themes } from '$lib/types/appearanceTypes';
	import { getToastStore, SlideToggle } from '@skeletonlabs/skeleton';
	import type { PageData } from './$types';

	// Page data injected from server response
	export let data: PageData;

	// Set the page title
	title.set('Appearance');

	// Initialise the toast store for notifications
	const toastStore = getToastStore();

	// Destructure appearance data from server response
	const themes = data.themes;
	const boards = data.boards;
	const pieces = data.pieces;

	// Initialise form bound variables with user's appearance data
	let theme: Themes = data.appearance.theme;
	let board: Boards = data.appearance.board;
	let piece: Pieces = data.appearance.piece;
	let dark: boolean = data.appearance.dark;

	// Track whether changes have been made to the form
	let changesMade: boolean = false;

	// Update page's dark mode to be same as dark variable
	function updateDark() {
		dark
			? document.documentElement.classList.add('dark')
			: document.documentElement.classList.remove('dark');
	}

	// Update page's theme to be same as theme variable
	function updateTheme() {
		document.body.setAttribute('data-theme', theme);
	}

	// Save the changes made to the user's appearance
	async function saveChanges() {
		// Send PATCH request to update user appearance
		const resp = await fetch('/appearance/saveChanges', {
			method: 'PATCH',
			headers: {
				accept: 'application/json'
			},
			body: JSON.stringify({
				theme: theme,
				board: board,
				piece: piece,
				dark: dark
			})
		});

		// Handle if response is ok with corresponding toast notification
		if (resp.ok) {
			changesMade = false;
			toastStore.trigger({
				message: 'Successfully updated account info!',
				background: 'variant-filled-success',
				timeout: 2000
			});
		} else {
			toastStore.trigger({
				message: 'Failed to update account info!',
				background: 'variant-filled-success',
				timeout: 2000
			});
		}
	}

	// Reset form values to the original profile data
	async function resetChanges() {
		changesMade = false;
		theme = data.appearance.theme;
		board = data.appearance.board;
		piece = data.appearance.piece;
		dark = data.appearance.dark;

		// Update page's dark mode and theme after resetting
		updateDark();
		updateTheme();
	}

	// Function called whenever a change is made
	// to check if form values differ from appearance data
	function onChange() {
		changesMade =
			board != data.appearance.board ||
			piece != data.appearance.piece ||
			theme != data.appearance.theme ||
			dark != data.appearance.dark;
	}
</script>

<div class="p-4 flex flex-col gap-3">
	<h2 class="h2">Appearance</h2>
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
		<div>
			<div>
				<!-- Theme selection dropdown -->
				<span>Theme</span>

				<select
					class="select"
					name="themeInput"
					bind:value={theme}
					on:change={() => {
						updateTheme();
						onChange();
					}}
				>
					{#each themes as theme}
						<option value={theme}>{theme}</option>
					{/each}
				</select>

				<!-- Dark mode slide toggle -->
				<SlideToggle
					name="dark-toggle"
					active="bg-primary-500"
					size="sm"
					bind:checked={dark}
					on:change={() => {
						updateDark();
						onChange();
					}}><span>Dark mode</span></SlideToggle
				>
			</div>

			<!-- Board selection dropdown -->
			<div>
				<span>Board</span>

				<select class="select" name="boardInput" bind:value={board} on:change={onChange}>
					{#each boards as board}
						<option value={board}>{board}</option>
					{/each}
				</select>
			</div>

			<!-- Pieces selection dropdown -->
			<div>
				<span>Pieces</span>

				<select class="select" name="pieceInput" bind:value={piece} on:change={onChange}>
					{#each pieces as piece}
						<option value={piece}>{piece}</option>
					{/each}
				</select>
			</div>
		</div>
		<div>
			<!-- Preview board -->
			<h3 class="h3">Preview</h3>
			<div class="size-64">
				<PreviewCg bind:piece bind:board></PreviewCg>
			</div>
		</div>
	</div>
	{#if changesMade}
		<div class="flex flex-row gap-3">
			<button on:click={saveChanges} type="submit" class="btn variant-filled-primary self-start"
				>Save changes</button
			>
			<button on:click={resetChanges} type="reset" class="btn variant-ghost-primary self-start"
				>Reset changes</button
			>
		</div>
	{/if}
</div>
