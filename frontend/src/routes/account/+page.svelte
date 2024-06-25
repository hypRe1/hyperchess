<script lang="ts">
    import type { PageData } from "./$types";
    import { Avatar, FileButton } from "@skeletonlabs/skeleton";
    import { getToastStore } from "@skeletonlabs/skeleton";
    import { title } from "$lib/store";

    title.set("Account details");

    const toastStore = getToastStore();

    export let data: PageData;

    let email: String = data.user.email;
    let about_me: String;
    if (!data.user.about_me) about_me = "";
    else about_me = data.user.about_me;
    let avatar = data.user.avatar;
    let country: String | null = data.user.country;
    let files: FileList;
    let changesMade: boolean = false;

    let countries = data.countries;

    $: {
        changesMade =
            email != data.user.email ||
            (about_me != data.user.about_me &&
                (about_me != "" || data.user.about_me != null)) ||
            avatar != data.user.avatar ||
            country != data.user.country;
    }

    function onImageUpload() {
        let file = files[0];
        let reader = new FileReader();
        avatar = reader.result;
        reader.onloadend = function () {
            avatar = reader.result;
        };
        reader.readAsDataURL(file);
    }

    async function removeImage() {
        const resp = await fetch(
            "http://127.0.0.1:8000/api/user/default_avatar",
        );
        avatar = "data:image/png;base64, " + (await resp.text()).slice(1, -1);
    }

    async function saveChanges() {
        const form = new FormData();
        form.append("file", avatar);

        const resp = await fetch("/account/saveChanges", {
            method: "PATCH",
            headers: {
                accept: "application/json",
            },
            body: JSON.stringify({
                avatar:
                    avatar != data.user.avatar
                        ? avatar.replace(/^data:image\/[a-z]+;base64,/, "")
                        : null,
                about_me: about_me,
                country: country,
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

    function resetChanges() {
        changesMade = false;
        email = data.user.email;
        if (!data.user.about_me) about_me = "";
        else about_me = data.user.about_me;
        avatar = data.user.avatar;
    }
</script>

<div class="p-4 flex flex-col gap-3">
    <h2 class="h2">Account details</h2>
    <div class="grid grid-cols-1 lg:grid-cols-2">
        <div class="p-4 flex flex-col gap-4">
            <label class="label">
                <span>Username</span>
                <input
                    class="input"
                    title="Username"
                    name="usernameInput"
                    type="text"
                    readonly={true}
                    value={data.user.username}
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
                            button="btn variant-filled-secondary"
                            >Upload</FileButton
                        >
                    </button>

                    <button
                        on:click={removeImage}
                        type="button"
                        class="btn variant-ghost-secondary">Remove</button
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
                    placeholder={data.user.email}
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
                    placeholder={data.user.about_me}
                    bind:value={about_me}
                />
            </label>

            <label class="label">
                <span>Country</span>

                <select class="select" name="countryInput" bind:value={country}>
                    <option value={null}>None</option>
                    {#each Object.entries(countries) as [code, country]}
                        <option value={code}>{country["name"]}</option>
                    {/each}
                </select>
            </label>
        </div>
        <div class="p-4 gap-3">
            <div class="card card-hover p-4 flex flex-row gap-3">
                <Avatar
                    src={avatar}
                    fallback="fallback_pfp.png"
                    width="w-32"
                    rounded="rounded-full"
                />
                <div>
                    <h2 class="h2">{data.user.username}</h2>
                    <p>{about_me}</p>
                </div>
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
