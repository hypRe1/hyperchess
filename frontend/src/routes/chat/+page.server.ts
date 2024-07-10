import type { RequestEvent } from "@sveltejs/kit";

export async function load(page: RequestEvent) {
    return { "token": page.cookies.get('token') }
}

export const ssr = false;