import type { RequestHandler } from './$types';

export const PATCH: RequestHandler = async ({ fetch, request }) => {
    const resp = await fetch("http://127.0.0.1:8000/api/user/profile", {
        method: "PATCH",
        headers: {
            accept: "application/json",
        },
        // @ts-ignore
        duplex: "half",
        body: request.body
    });
    return resp
};