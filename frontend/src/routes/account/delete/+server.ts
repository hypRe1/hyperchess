import type { RequestHandler } from './$types';

export const DELETE: RequestHandler = async ({ fetch, request }) => {
    const resp = await fetch("http://127.0.0.1:8000/api/user/", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            accept: "application/json",
        },
        // @ts-ignore
        duplex: "half",
        body: request.body
    });
    return resp
};