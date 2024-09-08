import type { MatchResponse } from "$lib/types/matchTypes";
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';


export const load: PageServerLoad = async ({ fetch, locals, params }) => {
    const profileResponse = await fetch(`http://127.0.0.1:8000/api/match/${params.id}`, { method: "GET" })
    if (!profileResponse.ok) {
        error(profileResponse.status, { message: profileResponse.statusText })
    }

    let match: MatchResponse = await profileResponse.json();

    return { "match": match, "appearance": locals.appearance }
}
