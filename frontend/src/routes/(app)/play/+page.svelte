<script>
	const matches = {
		hypre: { colour: null, time: 600, bonus: 0, handicapped: false, opp_time: 600, opp_bonus: 0 },
		manicminer123: {
			colour: null,
			time: 600,
			bonus: 0,
			handicapped: true,
			opp_time: 1,
			opp_bonus: 0
		}
	};

	import title from '$lib/title';
	$title = 'Play';
</script>

<h1 class="h1">Play</h1>

<div class="py-8">
	<h2 class="h2">Matches</h2>
	<div class="py-4">
		<button type="button" class="btn btn-sm variant-filled-primary">Create match listing</button>
		<button type="button" class="btn btn-sm variant-filled-warning">Delete match listing</button>
	</div>

	<nav class="list-nav py-4">
		<ul>
			<li>
				{#each Object.entries(matches) as [username, data]}
					<a href="/game">
						{#if data.handicapped}
							<span class="badge bg-secondary-500"
								>handicapped: opponent has {data.time} seconds {data.bonus} increment; You have {data.opp_time}
								seconds {data.bonus} increment</span
							>
						{:else}
							<span class="badge bg-primary-500">{data.time} seconds {data.bonus} increment</span>
						{/if}
						<span class="flex-auto">Rapid game vs {username}</span>
					</a>
				{/each}
			</li>
		</ul>
	</nav>
</div>
