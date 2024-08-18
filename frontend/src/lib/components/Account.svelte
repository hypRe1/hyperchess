<script lang="ts">
	import { Avatar, popup } from '@skeletonlabs/skeleton';
	import { page } from '$app/stores';

	export let avatar: string | undefined;
	export let username: string | undefined;
	export let admin: boolean = false;
	export let country: string | null = null;
	export let about_me: string | null | undefined = '';
	export let compact: boolean = true;

	console.log($page.data);

	let badges: { [badge: string]: string } = {};
	if (admin) {
		badges['Admin'] =
			'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjQiIHdpZHRoPSIyNCIgdmVyc2lvbj0iMS4xIiB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iPgogPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCAtMTAyOC40KSI+CiAgPGc+CiAgIDxwYXRoIGQ9Im01LjI4MTIgMS4yODEydjFsNC43MTg4IDQuNzE4OC0xIDMtMyAxLTQuNzE4OC00LjcxODhjLTAuMTYzOCAwLjU0NjYtMC4yODEyIDEuMTE4OC0wLjI4MTIgMS43MTg4IDAgMy4zMTQgMi42ODYzIDYgNiA2IDAuNiAwIDEuMTcyMS0wLjExNyAxLjcxODgtMC4yODEgMS43NjEyIDEuNzU5IDMuNTE5MiAzLjUyMiA1LjI4MTIgNS4yODFsNCA0YzAuNTEzIDAuNTEyIDEuMjE3IDAuODQ0IDIgMC44NDQgMS41NjcgMCAyLjg0NC0xLjI4MiAyLjg0NC0yLjg0NCAwLTAuNzgxLTAuMzMxLTEuNDg4LTAuODQ0LTJsLTQtNGMtMS43NjEtMS43Ni0zLjUyLTMuNTIxLTUuMjgxLTUuMjgxMiAwLjE2NC0wLjU0NjggMC4yODEtMS4xMTg4IDAuMjgxLTEuNzE4OCAwLTMuMzEzNy0yLjY4Ni02LTYtNi0wLjI0NTkgMC0wLjQ4MiAwLjAyNzktMC43MTg4IDAuMDYyNXYtMC43ODEzaC0xem0xNC43MTkgMTguMjE5YzAuODI4IDAgMS41IDAuNjcyIDEuNSAxLjVzLTAuNjcyIDEuNS0xLjUgMS41LTEuNS0wLjY3Mi0xLjUtMS41IDAuNjcyLTEuNSAxLjUtMS41eiIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCAxMDI4LjQpIiBmaWxsPSIjN2Y4YzhkIi8+CiAgIDxwYXRoIGZpbGw9IiM5NWE1YTYiIGQ9Im03IDEwMjkuNGMtMC42IDAtMS4xNzIxIDAuMS0xLjcxODggMC4ybDQuNzE4OCA0LjgtMSAzLTMgMS00LjcxODgtNC44Yy0wLjE2MzggMC42LTAuMjgxMiAxLjItMC4yODEyIDEuOCAwIDMuMyAyLjY4NjMgNiA2IDYgMC42IDAgMS4xNzIxLTAuMiAxLjcxODgtMC4zIDEuNzYxMiAxLjcgMy41MTkyIDMuNSA1LjI4MTIgNS4zbDQgNGMwLjUxMyAwLjUgMS4yMTcgMC44IDIgMC44IDEuNTY3IDAgMi44NDQtMS4zIDIuODQ0LTIuOCAwLTAuOC0wLjMzMS0xLjUtMC44NDQtMmwtNC00Yy0xLjc2MS0xLjgtMy41Mi0zLjYtNS4yODEtNS4zIDAuMTY0LTAuNiAwLjI4MS0xLjEgMC4yODEtMS43IDAtMy40LTIuNjg2LTYtNi02em0xMyAxNy41YzAuODI4IDAgMS41IDAuNiAxLjUgMS41IDAgMC44LTAuNjcyIDEuNS0xLjUgMS41cy0xLjUtMC43LTEuNS0xLjVjMC0wLjkgMC42NzItMS41IDEuNS0xLjV6Ii8+CiAgPC9nPgogPC9nPgo8L3N2Zz4K';
	}
	if (country != null) {
		let countryData = $page.data.countries[country];
		badges[countryData.name] = countryData.circular_image;
	}
</script>

<div class="{compact ? '' : 'card card-hover p-4'} flex flex-row gap-3">
	<Avatar
		src={avatar}
		fallback="fallback_pfp.png"
		width={compact ? 'w-12' : 'w-32'}
		rounded="rounded-full"
	/>
	<div>
		<div class="flex flex-row gap-1">
			<h1>{username}</h1>
			{#each Object.entries(badges) as [alt, badge]}
				<span
					class="badge-icon variant-filled [&>*]:pointer-events-none"
					use:popup={{
						event: 'hover',
						target: 'popupHover' + alt
					}}
				>
					<img src={badge} {alt} />
				</span>

				<div data-popup="popupHover{alt}">
					<div class="card p-1 variant-filled-secondary">
						<p>{alt}</p>
					</div>
				</div>
			{/each}
		</div>

		<p>{about_me}</p>
	</div>
</div>

<style>
	[data-popup] {
		transition-property: opacity;
		transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
		transition-duration: 0.15s;
	}

	.badge-icon:hover {
		/* Transitions */
		transition-delay: 1s;
		transition-duration: 1s;
		transform: rotate(360deg);
	}
</style>
