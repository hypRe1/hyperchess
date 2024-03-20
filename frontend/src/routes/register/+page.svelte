<script lang="ts">
    import { tokenStore } from "$lib/stores";
    import {
        getToastStore,
        type ToastSettings,
        getModalStore,
        type ModalSettings,
    } from "@skeletonlabs/skeleton";
    import { goto } from "$app/navigation";

    const toastStore = getToastStore();
    const modalStore = getModalStore();

    let username: string;
    let email: string;
    let password: string;
    let confirm_password: string;

    const registerSuccess: ToastSettings = {
        message: "Created an account successfully!",
        background: "variant-filled-success",
        timeout: 3000,
    };

    const registerCancelled: ToastSettings = {
        message: "Cancelled account creation!",
        background: "variant-filled-success",
        timeout: 3000,
    };

    const differentPasswords: ToastSettings = {
        message: "Passwords do not match",
        background: "variant-filled-error",
        timeout: 3000,
    };

    const alreadyLoggedIn: ToastSettings = {
        message: "You are already logged in!",
        background: "variant-filled-error",
        timeout: 3000,
    };

    const tooManyRequests: ToastSettings = {
        message: "You are sending too many requests!",
        background: "variant-filled-error",
        timeout: 3000,
    };

    const registerFailed: ToastSettings = {
        message: "Failed to sign up!",
        background: "variant-filled-error",
        timeout: 3000,
    };

    const loginFailed: ToastSettings = {
        message: "Failed to login!",
        background: "variant-filled-error",
        timeout: 2000,
    };

    const loginSuccess: ToastSettings = {
        message: "Logged in successfully!",
        background: "variant-filled-success",
        timeout: 2000,
    };

    const modal: ModalSettings = {
        type: "confirm",
        // Data
        title: "Please Confirm",
        body: "Are you sure you wish to proceed? You will not be able to change your username.",
        // TRUE if confirm pressed, FALSE if cancel pressed
        response: (r: boolean) => modalResponse(r),
    };

    async function modalResponse(r: boolean): Promise<void> {
        console.log(r);
        if (r) {
            await register();
        } else {
            toastStore.trigger(registerCancelled);
        }
    }

    async function registerConfirmation(): Promise<void> {
        if ($tokenStore !== "" && $tokenStore !== null) {
            toastStore.trigger(alreadyLoggedIn);
            return;
        }

        if (password !== confirm_password) {
            toastStore.trigger(differentPasswords);
            return;
        }

        modalStore.trigger(modal);
    }

    async function register(): Promise<void> {
        const response = await fetch("http://127.0.0.1:8000/api/user/", {
            method: "POST",
            body: `username=${username}&email=${email}&password=${password}`,
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        });

        if (response.status == 429) {
            toastStore.trigger(tooManyRequests);
            return;
        }

        if (!response.ok) {
            toastStore.trigger(registerFailed);
            return;
        }

        toastStore.trigger(registerSuccess);

        const loginResponse = await fetch(
            "http://127.0.0.1:8000/api/user/token",
            {
                method: "POST",
                body: `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`,
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            },
        );

        if (loginResponse.status == 429) {
            toastStore.trigger(tooManyRequests);
            return;
        }

        if (!loginResponse.ok) {
            toastStore.trigger(loginFailed);
            return;
        }

        if (loginResponse.body !== null) {
            const asJson = await loginResponse.json();
            const token = asJson.access_token;
            tokenStore.set(token);
            toastStore.trigger(loginSuccess);
            goto("/");
        }
    }
</script>

<div class="container h-full mx-auto gap-8 flex flex-col">
    <form class="card p-4 flex flex-col gap-3">
        <h2 class="h2">Sign up</h2>
        <input
            bind:value={username}
            id="username"
            name="username"
            class="input"
            title="Input (username)"
            type="text"
            placeholder="Username"
            required
            minlength="3"
            maxlength="32"
        />
        <input
            bind:value={email}
            id="email"
            name="email"
            class="input"
            title="Input (email)"
            type="email"
            placeholder="Email"
            autocomplete="email"
        />
        <input
            bind:value={password}
            id="password"
            name="password"
            class="input"
            title="Input (password)"
            type="password"
            placeholder="Password"
            required
            minlength="6"
            maxlength="125"
        />
        <input
            bind:value={confirm_password}
            id="confirm_password"
            name="confirm password"
            class="input"
            title="Input (confirm password)"
            type="password"
            placeholder="Confirm Password"
            required
            minlength="6"
            maxlength="125"
        />
        <button
            type="button"
            on:click={registerConfirmation}
            class="btn variant-ghost-primary self-start">Confirm</button
        >
    </form>
</div>
