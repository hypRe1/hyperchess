<script lang="ts">
	import Account from '$lib/components/Account.svelte';
	import { title } from '$lib/stores/title';
	import type { PersonalUserResponse } from '$lib/types/userTypes';
	import { FileButton, getToastStore } from '@skeletonlabs/skeleton';
	import { error } from '@sveltejs/kit';
	import type { PageData } from './$types';

	title.set('Account details');

	const toastStore = getToastStore();

	export let data: PageData;

	if (data.profile === undefined) error(500);
	let countries = data.countries;
	let profile: PersonalUserResponse = data.profile;

	let email: string = profile.email;
	let about_me: string;
	if (!profile.about_me) about_me = '';
	else about_me = profile.about_me;
	let avatar = profile.avatar;
	let country: string | null = profile.country;
	let files: FileList;
	let changesMade: boolean = false;

	$: {
		changesMade =
			email != profile.email ||
			(about_me != profile.about_me && (about_me != '' || profile.about_me != null)) ||
			avatar != profile.avatar ||
			country != profile.country;
	}

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

	async function removeImage() {
		const resp = await fetch('http://127.0.0.1:8000/api/user/default_avatar');
		avatar = await resp.json();
	}

	async function saveChanges() {
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

	function resetChanges() {
		changesMade = false;
		email = profile.email;
		if (!profile.about_me) about_me = '';
		else about_me = profile.about_me;
		avatar = profile.avatar;
	}
</script>

<div class="p-4 flex flex-col gap-3">
	<h2 class="h2">Account details</h2>
	<div class="grid grid-cols-1 lg:grid-cols-2">
		<div class="p-4 flex flex-col gap-4">
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
