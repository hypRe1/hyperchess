import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, locals }) => {
    const enginesResponse = await fetch("http://127.0.0.1:8000/api/engine/available", {
        method: "GET",
        headers: {
            accept: 'application/json'
        }
    })

    const engines: string[] = await enginesResponse.json()

    return { "engines": engines, "board": locals.board, "piece": locals.piece }
}
