<script lang="ts">
    import type { PageData } from "./$types";
    import type {
        MatchListing,
        MatchListingRequestForm,
    } from "$lib/types/gameConnectionManagerTypes";
    import {
        getToastStore,
        getModalStore,
        type ModalComponent,
        type ModalSettings,
    } from "@skeletonlabs/skeleton";
    import CreateMatchModal from "$lib/modals/createMatch.svelte";
    import FullScreenModal from "$lib/modals/fullScreen.svelte";
    import { browser } from "$app/environment";

    export let data: PageData;

    const toastStore = getToastStore();
    const modalStore = getModalStore();

    let listings: MatchListing[] = [];
    let userListing: MatchListing | null = null;

    let ws: WebSocket;

    if (browser) {
        ws = new WebSocket(`ws://127.0.0.1:8000/api/match/ws`);
        ws.onopen = function (event) {
            console.log("Connected to websocket");
        };

        ws.onmessage = function (event) {
            const msg = JSON.parse(event.data);
            let cmd = msg[0];
            let msgData = msg[1];

            switch (cmd) {
                case "tokenRequest":
                    if (data.token !== undefined) {
                        ws.send(data.token);
                    }
                    break;
                case "connected":
                    ws.send(JSON.stringify(["listenListings"]));
                    break;
                case "disconnected":
                    const modal: ModalSettings = {
                        type: "component",
                        component: { ref: FullScreenModal },
                        title: "Disconnected",
                        body: msgData["details"],
                        backdropClasses: "!p-0",
                    };
                    modalStore.trigger(modal);
                    break;
                case "addListing":
                    if (msgData.success) {
                        userListing = msgData.listing;
                        toastStore.trigger({
                            message: `Created listing with code ${msgData.listing.code}`,
                            background: "variant-filled-success",
                            timeout: 2000,
                        });
                    } else {
                        toastStore.trigger({
                            message: msgData.detail,
                            background: "variant-filled-error",
                            timeout: 2000,
                        });
                    }
                    break;
                case "removeListing":
                    if (msgData.success) {
                        userListing = null;
                        toastStore.trigger({
                            message: `Deleted listing with code ${msgData.code}`,
                            background: "variant-filled-success",
                            timeout: 2000,
                        });
                    } else {
                        toastStore.trigger({
                            message: msgData.detail,
                            background: "variant-filled-error",
                            timeout: 2000,
                        });
                    }
                    break;
                case "listenListings":
                    if (msgData.listings !== undefined) {
                        listings = msgData.listings;
                    } else if (msgData.addListing !== undefined) {
                        listings = [...listings, msgData.addListing];
                    } else if (msgData.removeListing !== undefined) {
                        listings = listings.filter((x) => {
                            return x.code !== msgData.removeListing;
                        });
                    }
                    break;
            }
        };
    }

    function createListing(listingForm: MatchListingRequestForm) {
        console.log(listingForm);
        ws.send(JSON.stringify(["addListing", listingForm]));
    }

    function createListingBtn() {
        const c: ModalComponent = { ref: CreateMatchModal };
        const modal: ModalSettings = {
            type: "component",
            component: c,
            title: "Create Match",
            response: (r) =>
                typeof r !== "undefined" && r !== false
                    ? createListing(r)
                    : null,
        };
        modalStore.trigger(modal);
    }

    function deleteListingBtn() {
        ws.send(JSON.stringify(["removeListing"]));
    }

    function getColourString(colour: boolean | null): string {
        if (colour === null) {
            return "random";
        } else if (colour) {
            return "white";
        } else {
            return "black";
        }
    }
</script>

<h2 class="h2">Play chess</h2>
<button
    on:click={createListingBtn}
    type="button"
    class="btn variant-filled-primary">Create Match</button
>
<button
    on:click={deleteListingBtn}
    type="button"
    class="btn variant-filled-primary">Delete Match</button
>

<!-- Responsive Container (recommended) -->
<div class="table-container">
    <!-- Native Table Element -->
    <table class="table table-interactive">
        <thead>
            <tr>
                <th>Code</th>
                <th>Colour</th>
                <th>Player</th>
                <th>Rating</th>
                <th>Time</th>
                <th>Mode</th>
            </tr>
        </thead>
        <tbody>
            {#if userListing !== null}
                <tr class="variant-ghost-secondary">
                    <td
                        ><span class="badge variant-soft-primary"
                            >{userListing.code}</span
                        ></td
                    >
                    <td>{getColourString(userListing.colour)}</td>
                    <td>{userListing.creator}</td>
                    <td>blank</td>
                    <td>{userListing.time}+{userListing.bonus}</td>
                    <td>blank</td>
                </tr>
            {/if}

            {#each listings as listing}
                {#if userListing == null || listing.code !== userListing.code}
                    <tr>
                        <td
                            ><span class="badge variant-soft-primary"
                                >{listing.code}</span
                            ></td
                        >
                        <td>{getColourString(listing.colour)}</td>
                        <td>{listing.creator}</td>
                        <td>blank</td>
                        <td>{listing.time}+{listing.bonus}</td>
                        <td>blank</td>
                    </tr>
                {/if}
            {/each}
        </tbody>
    </table>
</div>
