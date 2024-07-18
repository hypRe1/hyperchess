<script lang="ts">
    import type { SvelteComponent } from "svelte";
    import { goto } from "$app/navigation";

    // Stores
    import { getModalStore } from "@skeletonlabs/skeleton";

    // Props
    /** Exposes parent props to this component. */
    export let parent: SvelteComponent;

    const modalStore = getModalStore();

    // Notes: Use `w-screen h-screen` to fit the visible canvas size.
    const cBase =
        "bg-surface-100-800-token w-screen h-screen p-4 flex justify-center items-center";

    function reloadPage() {
        window.location.pathname = window.location.pathname;
        parent.onClose();
    }
</script>

{#if $modalStore[0]}
    <div class="modal-example-fullscreen {cBase}">
        <div class="flex flex-col items-center space-y-4">
            <h2 class="h2">{$modalStore[0].title}</h2>
            <p>{$modalStore[0].body}</p>
            <button class="btn variant-filled" on:click={reloadPage}
                >⟳ Refresh</button
            >
        </div>
    </div>
{/if}
