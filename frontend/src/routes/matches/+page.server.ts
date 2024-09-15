import type { MatchesResponse } from "$lib/types/matchTypes";
import type { PageServerLoad } from './$types';

// Fetch matches played on page load
export const load: PageServerLoad = async ({ fetch, locals }) => {
    const profileResponse = await fetch("http://127.0.0.1:8000/api/match/", { method: "GET" })
    let matches: MatchesResponse[] = await profileResponse.json();
    return { "matches": matches, "appearance": locals.appearance }
}
