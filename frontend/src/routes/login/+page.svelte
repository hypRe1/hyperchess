<script lang="ts">
    import { tokenStore } from "$lib/stores";
    import { getToastStore, type ToastSettings } from "@skeletonlabs/skeleton";
    import { goto } from "$app/navigation";

    const toastStore = getToastStore();

    let username: string;
    let password: string;

    const loginSuccess: ToastSettings = {
        message: "Logged in successfully!",
        background: "variant-filled-success",
        timeout: 2000,
    };

    const alreadyLoggedIn: ToastSettings = {
        message: "You are already logged in!",
        background: "variant-filled-error",
        timeout: 2000,
    };

    const tooManyRequests: ToastSettings = {
        message: "You are sending too many requests!",
        background: "variant-filled-error",
        timeout: 2000,
    };

    const loginFailed: ToastSettings = {
        message: "Failed to login!",
        background: "variant-filled-error",
        timeout: 2000,
    };

    async function login(): Promise<void> {
        if ($tokenStore !== "" && $tokenStore !== null) {
            toastStore.trigger(alreadyLoggedIn);
            return;
        }

        const response = await fetch("http://127.0.0.1:8000/api/user/token", {
            method: "POST",
            body: `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`,
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        });

        if (response.status == 429) {
            toastStore.trigger(tooManyRequests);
            return;
        }

        if (!response.ok) {
            toastStore.trigger(loginFailed);
            return;
        }

        if (response.body !== null) {
            const asJson = await response.json();
            const token = asJson.access_token;
            tokenStore.set(token);
            toastStore.trigger(loginSuccess);
            goto("/");
        }
    }
</script>

<div class="container h-full mx-auto gap-8 flex flex-col">
    <form class="card p-4 flex flex-col gap-3">
        <h2 class="h2">Login</h2>
        <input
            bind:value={username}
            class="input"
            title="Input (username)"
            type="text"
            placeholder="Username"
        />
        <input
            bind:value={password}
            class="input"
            title="Input (password)"
            type="password"
            placeholder="Password"
        />
        <button
            type="button"
            on:click={login}
            class="btn variant-ghost-primary self-start">Confirm</button
        >
        <h3 class="h5">Or if you do not have an account</h3>
        <a
            href="/register"
            class="btn variant-ghost-secondary self-start"
            data-sveltekit-preload-data="hover">Sign up</a
        >
    </form>
</div>
