<script lang="ts">
    import { Avatar } from "@skeletonlabs/skeleton";
    import { page } from "$app/stores";

    let messages: {
        username: string;
        avatar: string;
        content: string;
        isHost: boolean;
    }[] = [];
    let users = 0;
    let currentMessage = "";

    let ws = new WebSocket(
        `ws://127.0.0.1:8000/api/chat/ws/${$page.data.username}`,
    );

    ws.onopen = function (event) {
        ws.send(
            JSON.stringify([
                "joinRoom",
                {
                    username: $page.data.username,
                    avatar: $page.data.avatar,
                },
            ]),
        );
        console.log("Joined chat room");
    };

    let elemChat: HTMLElement;
    function scrollChatBottom(behavior?: ScrollBehavior): void {
        elemChat.scrollTo({ top: elemChat.scrollHeight, behavior });
    }

    ws.onmessage = function (event) {
        const msg = JSON.parse(event.data);

        if (msg[0] == "joinRoom") {
            console.log("join room");
            const newMessage = {
                username: "Server",
                avatar: msg[1]["avatar"],
                content: `${msg[1]["username"]} joined the chat room`,
                isHost: msg[1]["username"] == $page.data.username,
            };
            messages = [...messages, newMessage];
            setTimeout(() => {
                scrollChatBottom("smooth");
            }, 0);
        } else if (msg[0] == "sendMessage") {
            const newMessage = {
                username: msg[1]["username"],
                avatar: msg[1]["avatar"],
                content: msg[1]["content"],
                isHost: msg[1]["username"] == $page.data.username,
            };
            messages = [...messages, newMessage];
            setTimeout(() => {
                scrollChatBottom("smooth");
            }, 0);
        } else if (msg[0] == "roomData") {
            users = msg[1]["users"];
        }
    };

    function send_message() {
        ws.send(
            JSON.stringify([
                "sendMessage",
                {
                    username: $page.data.username,
                    avatar: $page.data.avatar,
                    content: currentMessage,
                },
            ]),
        );
        currentMessage = "";
    }
</script>

<h2 class="h2">Chat room ({users} users)</h2>

<div class="space-y-4 overflow-y-auto" bind:this={elemChat}>
    {#each messages as msg}
        {#if msg.isHost}
            <div class="grid grid-cols-[1fr_auto] gap-2">
                <div
                    class="card p-4 rounded-tr-none space-y-2 variant-soft-primary"
                >
                    <header class="flex justify-between items-center">
                        <p class="font-bold">{msg.username}</p>
                        <small class="opacity-50">A few seconds ago</small>
                    </header>
                    <p>{msg.content}</p>
                </div>
                <Avatar src={msg.avatar} width="w-12" />
            </div>
        {:else}
            <div class="grid grid-cols-[auto_1fr] gap-2">
                <Avatar src={msg.avatar} width="w-12" />
                <div class="card p-4 variant-soft rounded-tl-none space-y-2">
                    <header class="flex justify-between items-center">
                        <p class="font-bold">{msg.username}</p>
                        <small class="opacity-50">A few seconds ago</small>
                    </header>
                    <p>{msg.content}</p>
                </div>
            </div>
        {/if}
    {/each}
</div>

<form
    on:submit|preventDefault
    class="input-group input-group-divider grid-cols-[88%_12%] w-4/5 place-content-center rounded-container-token fixed bottom-5"
>
    <input
        bind:value={currentMessage}
        class="bg-transparent border-0 ring-0"
        name="prompt"
        id="prompt"
        placeholder="Write a message..."
    />
    <button class="variant-filled-primary" on:click={send_message}>Send</button>
</form>
