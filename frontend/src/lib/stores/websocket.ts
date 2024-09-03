import { get, writable } from 'svelte/store';

export enum ConnectionState {
    MATCH_PLAYING,
    MATCH_SPECTATING,
    LISTENING_LISTINGS,
    LISTENING_MATCHES
}
interface WebSocketStore {
    socket: WebSocket | null;
    states: Set<ConnectionState>;
    onMessageHandler: ((event: MessageEvent) => void);
}

const initialState: WebSocketStore = {
    socket: null,
    states: new Set<ConnectionState>(),
    onMessageHandler: () => null
};

export const socketStore = writable<WebSocketStore>(initialState);

export const connectSocket = (onMessage: (message: MessageEvent) => void) => {
    socketStore.update((state) => {
        if (state.socket && state.socket.readyState === WebSocket.OPEN) {
            // Reuse existing socket
            state.onMessageHandler = onMessage
            return state;
        }

        // Create a new socket
        const socket = new WebSocket("ws://127.0.0.1:8000/api/match/ws");

        socket.onopen = () => {
            // console.log('WebSocket connection established');
        };

        socket.onmessage = (event) => {
            state.onMessageHandler(event);
        };

        socket.onclose = () => {
            // console.log('WebSocket connection closed');
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
            // console.log('WebSocket connection closed from store');
        }
        return initialState;
    });
};

export const addConnectionState = (connState: ConnectionState) => {
    socketStore.update((state) => {
        state.states.add(connState);
        return state;
    })
}

export const removeConnectionState = (connState: ConnectionState) => {
    socketStore.update((state) => {
        state.states.delete(connState);
        return state;
    })
}

export const hasConnectionState = (connState: ConnectionState) => {
    let wsStore = get(socketStore);
    return wsStore.states.has(connState);
}