<script lang="ts">
    import ChessBoard from "$lib/components/ChessBoard.svelte";
    import { Avatar } from "@skeletonlabs/skeleton";
    import { type Move } from "chess.js";
    import { page } from "$app/stores";
    import { title } from "$lib/store";
    import type { PageData } from "./$types";

    export let data: PageData;

    title.set("Play vs hyperfish");

    let engine: String = "hyperfish";
    let depth: number = 5;
    let fen: string =
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    let undo: () => void;
    let flipBoard: () => void;
    let reset: () => void;
    let load_fen: (fen: string) => void;
    // let history: () => Move[] | undefined;

    function engineChange() {
        if (depth > 8 && engine == "hyperfish") {
            depth = 8;
        }
    }

    function fen_btn() {
        load_fen(fen);
    }
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <div class="size-11/12">
        <div class="p-4 flex flex-row gap-3">
            <Avatar
                src="https://static-00.iconduck.com/assets.00/fish-icon-1982x2048-xxayvvtg.png"
                width="w-14"
                rounded="rounded-full"
            />
            <div>
                <h4 class="h4">{engine}</h4>
                <p>The powerful chess engine</p>
            </div>
        </div>
        <ChessBoard
            bind:depth
            bind:engine
            bind:undo
            bind:flipBoard
            bind:reset
            bind:load_fen
        ></ChessBoard>
        <div class="p-4 flex flex-row gap-3">
            <Avatar
                src={$page.data.avatar}
                width="w-14"
                rounded="rounded-full"
            />
            <div>
                <h4 class="h4">{$page.data.username}</h4>
                <p>{$page.data.about_me}</p>
            </div>
        </div>
    </div>
    <div class="card p-5 gap-3">
        <h2 class="h2">Chess engine demo</h2>
        <div class="space-y-4 py-5">
            <label class="label">
                <span>Select Engine</span>
                <select
                    class="select"
                    bind:value={engine}
                    on:change={engineChange}
                    name="engineSelect"
                >
                    {#each Object.entries(data.engines) as [i, name]}
                        <option value={name}>{name}</option>
                    {/each}
                </select>
            </label>
            <label class="label">
                <span>Engine depth: {depth}</span>
                <input
                    type="range"
                    min="1"
                    max={engine == "hyperfish" ? 8 : 20}
                    bind:value={depth}
                />
            </label>
            <!-- <p>
                {history()}
            </p> -->
            <button
                on:click={undo}
                type="button"
                class="btn variant-ghost self-start">Undo</button
            >
            <button
                on:click={flipBoard}
                type="button"
                class="btn variant-ghost self-start">Flip</button
            >
            <button
                on:click={reset}
                type="button"
                class="btn variant-ghost self-start">Reset</button
            >
            <label class="label">
                <span>Fen</span>
                <div class="space-y-2">
                    <input class="textarea" name="fenInput" bind:value={fen} />
                    <button
                        on:click={fen_btn}
                        type="button"
                        class="btn variant-ghost self-start">Load fen</button
                    >
                </div>
            </label>
        </div>
    </div>
</div>
