<script lang="ts">
    import { Avatar } from "@skeletonlabs/skeleton";
    import { page } from "$app/stores";

    enum msgType {
        SERVER,
        HOST,
        PEER,
    }

    type Message = {
        username: string;
        avatar: string;
        content: string;
        type: msgType;
        time: string;
    };

    let messages: Message[] = [];
    let users = 0;
    let currentMessage = "";
    let elemChat: HTMLElement;

    let ws = new WebSocket(`ws://127.0.0.1:8000/api/chat/ws`);

    ws.onopen = function (event) {
        ws.send($page.data.token);
        console.log("Joined chat room");
    };

    function scrollChatBottom(behavior?: ScrollBehavior): void {
        elemChat.scrollTo({ top: elemChat.scrollHeight, behavior });
    }

    function getTime(): string {
        let t = new Date();
        return `${`0${t.getHours()}`.slice(-2)}:${`0${t.getMinutes()}`.slice(-2)}:${`0${t.getSeconds()}`.slice(-2)}`;
    }

    function addMsg(msg: Message): void {
        messages = [...messages, msg];
        setTimeout(() => {
            scrollChatBottom("smooth");
        }, 0);
    }

    ws.onmessage = function (event) {
        const msg = JSON.parse(event.data);

        if (msg[0] == "joinRoom") {
            addMsg({
                username: "Server",
                avatar: msg[1]["avatar"],
                content: `${msg[1]["username"]} joined the chat room`,
                type: msgType.SERVER,
                time: getTime(),
            });
        } else if (msg[0] == "leaveRoom") {
            addMsg({
                username: "Server",
                avatar: msg[1]["avatar"],
                content: `${msg[1]["username"]} left the chat room`,
                type: msgType.SERVER,
                time: getTime(),
            });
        } else if (msg[0] == "serverMessage") {
            addMsg({
                username: "Server",
                avatar: $page.data.avatar,
                content: msg[1]["content"],
                type: msgType.SERVER,
                time: getTime(),
            });
        } else if (msg[0] == "sendMessage") {
            addMsg({
                username: msg[1]["username"],
                avatar: msg[1]["avatar"],
                content: msg[1]["content"],
                type:
                    msg[1]["username"] == $page.data.username
                        ? msgType.HOST
                        : msgType.PEER,
                time: getTime(),
            });
        } else if (msg[0] == "roomData") {
            users = msg[1]["users"];
        }
    };

    function send_message() {
        if (currentMessage.replace(/\s/g, "").length) {
            ws.send(
                JSON.stringify([
                    "sendMessage",
                    {
                        content: currentMessage,
                    },
                ]),
            );
            currentMessage = "";
        }
    }
</script>

<div class="chat w-full h-full">
    <div class="grid grid-row-[1fr_auto]">
        <h2 class="h2">Chat room ({users} users)</h2>
        <section
            class="max-h-[500px] p-4 overflow-y-auto space-y-4"
            bind:this={elemChat}
        >
            {#each messages as msg}
                {#if msg.type == msgType.HOST}
                    <div class="grid grid-cols-[1fr_auto] gap-2">
                        <div
                            class="card p-4 rounded-tr-none space-y-2 variant-soft-primary"
                        >
                            <header class="flex justify-between items-center">
                                <p class="font-bold">{msg.username}</p>
                                <small class="opacity-50">{msg.time}</small>
                            </header>
                            <p>{msg.content}</p>
                        </div>
                        <Avatar src={msg.avatar} width="w-12" />
                    </div>
                {:else if msg.type == msgType.PEER}
                    <div class="grid grid-cols-[auto_1fr] gap-2">
                        <Avatar src={msg.avatar} width="w-12" />
                        <div
                            class="card p-4 variant-soft rounded-tl-none space-y-2"
                        >
                            <header class="flex justify-between items-center">
                                <p class="font-bold">{msg.username}</p>
                                <small class="opacity-50">{msg.time}</small>
                            </header>
                            <p>{msg.content}</p>
                        </div>
                    </div>
                {:else if msg.type == msgType.SERVER}
                    <div
                        class="p-4 variant-soft-secondary rounded-tl-none space-y-2 flex flex-row gap-x-4"
                    >
                        <Avatar src={msg.avatar} width="w-12" />
                        <p>
                            <small class="opacity-50">{msg.time}</small>
                            {msg.content}
                        </p>
                    </div>
                {/if}
            {/each}
        </section>
        <!-- Prompt -->
        <section class="border-t border-surface-500/30 p-4">
            <form
                on:submit|preventDefault
                class="input-group input-group-divider flex flex-row rounded-container-token"
            >
                <input
                    bind:value={currentMessage}
                    class="bg-transparent border-0 ring-0 grow"
                    name="prompt"
                    id="prompt"
                    placeholder="Write a message..."
                />
                <button class="variant-filled-primary" on:click={send_message}
                    ><svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        fill="currentColor"
                        class="bi bi-send"
                        viewBox="0 0 16 16"
                    >
                        <path
                            d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"
                        />
                    </svg></button
                >
            </form>
        </section>
    </div>
</div>
