import type { MatchResponse } from "$lib/types/matchTypes";
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Action, Actions } from './$types'


export const load: PageServerLoad = async ({ fetch, locals, params }) => {
    const profileResponse = await fetch(`http://127.0.0.1:8000/api/match/${params.id}`, { method: "GET" })
    const enginesResponse = await fetch("http://127.0.0.1:8000/api/engine/available", { method: "GET" })
    if (!profileResponse.ok) {
        error(profileResponse.status, { message: profileResponse.statusText })
    }

    let match: MatchResponse = await profileResponse.json();
    const engines: string[] = await enginesResponse.json()

    return { "match": match, "appearance": locals.appearance, "engines": engines }
}


const analysis: Action = async ({ fetch, request, params }) => {
    const data = await request.formData()

    const body = JSON.stringify({
        "engine": data.get("engine"),
        "match_id": Number(params.id),
        "depth": Number(data.get("depth")),
    })

    const response = await fetch('http://127.0.0.1:8000/api/engine/review_match', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: body
    });

    const asJson = await response.json();

    return asJson
}

export const actions: Actions = { default: analysis }
