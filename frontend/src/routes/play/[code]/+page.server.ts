import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, locals }) => {
    const boardsResponse = await fetch("http://127.0.0.1:8000/api/appearance/boards", { method: "GET" })
    const piecesResponse = await fetch("http://127.0.0.1:8000/api/appearance/pieces", { method: "GET" })
    const enginesResponse = await fetch("http://127.0.0.1:8000/api/engine/available", { method: "GET" })

    const boards: string[] = await boardsResponse.json()
    const pieces: string[] = await piecesResponse.json()
    const engines: string[] = await enginesResponse.json()

    return {
        engines: engines,
        board: locals.appearance.board,
        piece: locals.appearance.piece,
        boards: boards,
        pieces: pieces
    }
}
