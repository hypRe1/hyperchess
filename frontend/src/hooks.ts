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
    return await resolve(event)
};
