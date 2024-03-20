<script lang="ts">
    import { Table, tableMapperValues } from "@skeletonlabs/skeleton";
    import type { TableSource } from "@skeletonlabs/skeleton";

    const sourceData = [
        { time: "10m", type: "Rapid", started: false, users: "hypre" },
        { time: "1m", type: "Bullet", started: false, users: "jam" },
        { time: "3m+5s", type: "Blitz", started: false, users: "nomad188" },
    ];

    const tableSimple: TableSource = {
        // A list of heading labels.
        head: ["Time", "Type", "Started", "Users"],
        // The data visibly shown in your table body UI.
        body: tableMapperValues(sourceData, [
            "time",
            "type",
            "started",
            "users",
        ]),
        // Optional: The data returned when interactive is enabled and a row is clicked.
        meta: tableMapperValues(sourceData, [
            "position",
            "name",
            "symbol",
            "weight",
        ]),
    };
</script>

<nav class="list-nav">
    <h2 class="h2">Matches</h2>
    <div class="py-4">
        <a
            href="/"
            class="btn variant-ghost-primary"
            data-sveltekit-preload-data="hover">Create match</a
        >
        <a
            href="/"
            class="btn variant-ghost-secondary"
            data-sveltekit-preload-data="hover">Join match</a
        >
    </div>
    <Table source={tableSimple} />
</nav>
