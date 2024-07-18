import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ locals }) => {
    const themesResponse = await fetch("http://127.0.0.1:8000/api/appearance/themes", { method: "GET" })
    const boardsResponse = await fetch("http://127.0.0.1:8000/api/appearance/boards", { method: "GET" })
    const piecesResponse = await fetch("http://127.0.0.1:8000/api/appearance/pieces", { method: "GET" })

    const themes: string[] = await themesResponse.json()
    const boards: string[] = await boardsResponse.json()
    const pieces: string[] = await piecesResponse.json()

    return {
        appearance: locals.appearance,
        themes: themes,
        boards: boards,
        pieces: pieces
    }
}

export const ssr = false;