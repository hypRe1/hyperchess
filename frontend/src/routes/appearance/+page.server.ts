import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ locals, fetch }) => {
    const appearanceResp = await fetch("appearances.json")
    const appearance = await appearanceResp.json()

    return {
        appearance: locals.appearance,
        themes: appearance.themes,
        boards: appearance.boards,
        pieces: appearance.pieces
    }
}

export const ssr = false;