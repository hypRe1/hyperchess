<script lang="ts">
	import Account from '$lib/components/Account.svelte';
	import { title } from '$lib/stores/title';
	import type { PersonalUserResponse } from '$lib/types/userTypes';
	import { FileButton, getToastStore } from '@skeletonlabs/skeleton';
	import { error } from '@sveltejs/kit';
	import type { PageData } from './$types';

	// Page data injected from server response
	export let data: PageData;

	// Set the page title
	title.set('Account details');

	// Initialise toast store for notifications
	const toastStore = getToastStore();

	// Error handling in the case that
	if (data.profile === undefined) error(500);

	// Destructure profile data from server response
	let countries = data.countries;
	let profile: PersonalUserResponse = data.profile;

	// Initialise form bound variables with user data
	let email: string = profile.email;
	let about_me: string;
	if (!profile.about_me)
		about_me = ''; // Default to empty if user has not about me
	else about_me = profile.about_me;
	let avatar = profile.avatar;
	let country: string | null = profile.country;
	let files: FileList;

	// Track whether changes have been made to the form
	let changesMade: boolean = false;

	// Reactive statement to check if form values differ from profile data
	$: {
		changesMade =
			email != profile.email ||
			(about_me != profile.about_me && (about_me != '' || profile.about_me != null)) ||
			avatar != profile.avatar ||
			country != profile.country;
	}

	// Handle image file upload, updating avatar with the base64 encoded image
	function onImageUpload() {
		let file = files[0];
		let reader = new FileReader();
		reader.onloadend = function () {
			if (typeof reader.result === 'string') {
				avatar = reader.result;
			}
		};
		reader.readAsDataURL(file);
	}

	// Reset avatar to the default by fetching it from the server
	async function removeImage() {
		const resp = await fetch('http://127.0.0.1:8000/api/user/default_avatar');
		avatar = await resp.json();
	}

	// Save the changes made to the account
	async function saveChanges() {
		// Send PATCH request to update user info
		const resp = await fetch('/account/saveChanges', {
			method: 'PATCH',
			headers: {
				accept: 'application/json'
			},
			body: JSON.stringify({
				avatar: avatar != profile.avatar ? avatar.replace(/^data:image\/[a-z]+;base64,/, '') : null,
				about_me: about_me,
				country: country
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
	function resetChanges() {
		changesMade = false;
		email = profile.email;
		if (!profile.about_me) about_me = '';
		else about_me = profile.about_me;
		avatar = profile.avatar;
		country = profile.country;
	}
</script>

<div class="p-4 flex flex-col gap-3">
	<h2 class="h2">Account details</h2>
	<div class="grid grid-cols-1 lg:grid-cols-2">
		<div class="p-4 flex flex-col gap-4">
			<!-- Display username (read-only) -->
			<label class="label">
				<span>Username (cannot be changed)</span>
				<input
					class="input"
					title="Username"
					name="usernameInput"
					type="text"
					readonly={true}
					value={profile.username}
				/>
			</label>

			<!-- Avatar upload and remove functionality -->
			<label>
				<span>Avatar</span>
				<div class="flex flex-row gap-1">
					<button type="button">
						<FileButton
							bind:files
							on:change={onImageUpload}
							name="files"
							accept="image/png, image/jpeg"
							button="btn variant-filled-secondary">Upload</FileButton
						>
					</button>

					<button on:click={removeImage} type="button" class="btn variant-ghost-secondary"
						>Remove</button
					>
				</div>
			</label>

			<!-- Email input field -->
			<label class="label">
				<span>Email</span>
				<input
					class="input"
					title="Email"
					name="emailInput"
					type="email"
					placeholder={profile.email}
					autocomplete="email"
					bind:value={email}
				/>
			</label>

			<!-- About me textarea input -->
			<label class="label">
				<span>About me</span>
				<textarea
					class="textarea"
					name="aboutMeInput"
					rows="4"
					placeholder={profile.about_me}
					bind:value={about_me}
				/>
			</label>

			<!-- Country selection dropdown -->
			<label class="label">
				<span>Country</span>

				<select class="select" name="countryInput" bind:value={country}>
					<option value={null}>None</option>
					{#each Object.entries(countries) as [code, country]}
						<option value={code}>{country.emoji} {country.name}</option>
					{/each}
				</select>
			</label>
		</div>

		<!-- Display account component with bound props -->
		<div>
			<Account
				bind:avatar
				bind:username={profile.username}
				bind:country
				bind:admin={profile.admin}
				bind:about_me
				compact={false}
			></Account>
		</div>
	</div>

	<!-- Show buttons for saving or resetting changes if changes are detected -->
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
