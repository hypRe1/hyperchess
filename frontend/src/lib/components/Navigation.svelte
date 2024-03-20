<script lang="ts">
    import { getDrawerStore } from "@skeletonlabs/skeleton";

    const drawerStore = getDrawerStore();

    function drawerClose(): void {
        drawerStore.close();
    }

    const pages = {
        Home: "/",
        Play: "/play",
        Train: "/?train",
        Analysis: "/?analysis",
        Leaderboard: "/?leaderboard",
    };
</script>

<nav class="list-nav p-4">
    <ul>
        {#each Object.entries(pages) as [title, url]}
            <li><a href={url} on:click={drawerClose}>{title}</a></li>
        {/each}
    </ul>
</nav>
