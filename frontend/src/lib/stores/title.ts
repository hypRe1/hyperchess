import { writable } from 'svelte/store';

function createTitle() {
    const { subscribe, set, update } = writable('');

    return {
        subscribe,
        set: (value: string) => {
            set(`${value} • Hyperchess`)
        },
        clear: () => {
            set('Hyperchess • chessssss');
        }
    }
}

export const title = createTitle();