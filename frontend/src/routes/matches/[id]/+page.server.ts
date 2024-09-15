import type { MatchResponse } from "$lib/types/matchTypes";
import { error } from '@sveltejs/kit';
import type { Action, Actions, PageServerLoad } from './$types';

// Get match and engines on page load
export const load: PageServerLoad = async ({ fetch, locals, params }) => {
    // Make GET requests for match details and available engines
    const matchResponse = await fetch(`http://127.0.0.1:8000/api/match/${params.id}`, { method: "GET" })
    const enginesResponse = await fetch("http://127.0.0.1:8000/api/engine/available", { method: "GET" })
    if (!matchResponse.ok) {
        error(matchResponse.status, { message: matchResponse.statusText })
    }

    // Parse JSON response from server
    let match: MatchResponse = await matchResponse.json();
    const engines: string[] = await enginesResponse.json()

    return { "match": match, "appearance": locals.appearance, "engines": engines }
}

// Handle engine analysis form
const analysis: Action = async ({ fetch, request, params }) => {
    // Retrieve form data from the request
    const data = await request.formData()

    const body = JSON.stringify({
        "engine": data.get("engine"),
        "match_id": Number(params.id),
        "depth": Number(data.get("depth")),
    })

    // Make a POST request to the review match endpoint
    const response = await fetch('http://127.0.0.1:8000/api/engine/review_match', {
        method: 'POST',
        headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: body
    });

    // Parse the JSON response from the server
    const asJson = await response.json();

    return asJson
}

export const actions: Actions = { default: analysis }
