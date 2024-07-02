import type { Handle, HandleFetch } from '@sveltejs/kit';

const unprotectedRoutes: string[] = [
    "/",
    "/login",
    "/register"
]

function redirect(location: string, body?: string) {
    return new Response(body, {
        status: 303,
        headers: { location }
    });
}


async function get_appearance(token: string | undefined) {
    if (!token) {
        return {
            "theme": "skeleton",
            "board": "blue",
            "piece": "staunty",
            "dark": true
        }
    }

    const resp = await fetch("http://127.0.0.1:8000/api/appearance", {
        method: "GET",
        headers: {
            accept: 'application/json',
            "Authorization": `Bearer ${token}`
        }
    })
    return await resp.json();
}

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
    const token = event.cookies.get('token');
    if (request.url.startsWith('http://127.0.0.1:8000/api/') && token) {
        request.headers.set('Authorization', `Bearer ${token}`);
    }

    const resp = await fetch(request);
    return resp
};

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token')
    if (!token && !unprotectedRoutes.includes(event.url.pathname)) return redirect('/login', 'User not authenticated')


    if (token) {
        event.locals.loggedIn = true
    }
    const appearance = await get_appearance(token);
    event.locals.board = appearance.board;
    event.locals.piece = appearance.piece;
    event.locals.theme = appearance.theme;
    event.locals.dark = appearance.dark;

    return await resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%theme%', appearance.theme).replace("%dark%", appearance.dark ? "dark" : "")
    })
};
