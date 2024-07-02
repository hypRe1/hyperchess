<script lang="ts">
    import { page } from "$app/stores";
    import { SlideToggle } from "@skeletonlabs/skeleton";
    import PreviewCg from "$lib/components/previewCG.svelte";
    import { getToastStore } from "@skeletonlabs/skeleton";
    import { title } from "$lib/store";

    title.set("Appearance");

    const toastStore = getToastStore();

    const themes = $page.data.themes;
    const boards = $page.data.boards;
    const pieces = $page.data.pieces;

    let theme: string = $page.data.theme;
    let board: string = $page.data.board;
    let piece: string = $page.data.piece;
    let dark: boolean = $page.data.dark;

    let changesMade: boolean = false;

    async function saveChanges() {
        const resp = await fetch("/appearance/saveChanges", {
            method: "PATCH",
            headers: {
                accept: "application/json",
            },
            body: JSON.stringify({
                theme: theme,
                board: board,
                piece: piece,
                dark: dark,
            }),
        });
        if (resp.ok) {
            changesMade = false;
            toastStore.trigger({
                message: "Successfully updated account info!",
                background: "variant-filled-success",
                timeout: 2000,
            });
        } else {
            toastStore.trigger({
                message: "Failed to update account info!",
                background: "variant-filled-success",
                timeout: 2000,
            });
        }
    }
    async function resetChanges() {
        theme = $page.data.theme;
        board = $page.data.board;
        piece = $page.data.piece;
        dark = $page.data.dark;
        changesMade = false;
        updateDark();
        updateTheme();
    }

    function updateDark() {
        dark
            ? document.documentElement.classList.add("dark")
            : document.documentElement.classList.remove("dark");

        onChange();
    }

    function updateTheme() {
        document.body.setAttribute("data-theme", theme);

        onChange();
    }

    function onChange() {
        changesMade =
            board != $page.data.board ||
            piece != $page.data.piece ||
            theme != $page.data.theme ||
            dark != $page.data.dark;
    }
</script>

<div class="p-4 flex flex-col gap-3">
    <h2 class="h2">Appearance</h2>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
            <!-- Form -->
            <div>
                <span>Theme</span>

                <select
                    class="select"
                    name="themeInput"
                    bind:value={theme}
                    on:change={updateTheme}
                >
                    {#each themes as theme}
                        <option value={theme}>{theme}</option>
                    {/each}
                </select>
                <SlideToggle
                    name="dark-toggle"
                    active="bg-primary-500"
                    size="sm"
                    bind:checked={dark}
                    on:change={updateDark}><span>Dark mode</span></SlideToggle
                >
            </div>
            <div>
                <span>Board</span>

                <select
                    class="select"
                    name="boardInput"
                    bind:value={board}
                    on:change={onChange}
                >
                    {#each boards as board}
                        <option value={board}>{board}</option>
                    {/each}
                </select>
            </div>
            <div>
                <span>Pieces</span>

                <select
                    class="select"
                    name="pieceInput"
                    bind:value={piece}
                    on:change={onChange}
                >
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
            <button
                on:click={saveChanges}
                type="submit"
                class="btn variant-filled-primary self-start"
                >Save changes</button
            >
            <button
                on:click={resetChanges}
                type="reset"
                class="btn variant-ghost-primary self-start"
                >Reset changes</button
            >
        </div>
    {/if}
</div>
