import { writable } from 'svelte/store';

interface WebSocketStore {
    socket: WebSocket | null;
    onMessageHandler: ((event: MessageEvent) => void);
}

const initialState: WebSocketStore = {
    socket: null,
    onMessageHandler: () => null
};

export const socketStore = writable<WebSocketStore>(initialState);

export const connectSocket = (url: string, onMessage: (message: MessageEvent) => void) => {
    socketStore.update((state) => {
        if (state.socket && state.socket.readyState === WebSocket.OPEN) {
            // Reuse existing socket
            state.onMessageHandler = onMessage
            return state;
        }

        // Create a new socket
        const socket = new WebSocket(url);

        socket.onopen = () => {
            console.log('WebSocket connection established');
        };

        socket.onmessage = (event) => {
            console.log('Message from server:', event.data);
            state.onMessageHandler(event);
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed');
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        state.socket = socket;
        state.onMessageHandler = onMessage;
        return state;
    });
};

export const sendMessage = (message: string) => {
    socketStore.update((state) => {
        if (state.socket && state.socket.readyState === WebSocket.OPEN) {
            state.socket.send(message);
        } else {
            console.error('WebSocket is not open');
        }
        return state;
    });
};

export const closeSocket = () => {
    socketStore.update((state) => {
        if (state.socket) {
            state.socket.close();
            console.log('WebSocket connection closed from store');
        }
        return initialState;
    });
};