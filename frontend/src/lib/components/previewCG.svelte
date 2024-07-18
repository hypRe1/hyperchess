<script lang="ts">
    import { Chessground } from "svelte-chessground";
    import CustomCG from "$lib/components/CustomCG.svelte";
    export let piece: string;
    export let board: string;

    let chessground: Chessground;

    let config = {
        viewOnly: true,
        coordinates: false,
    };
</script>

<CustomCG bind:chessground bind:piece bind:board {config} />
