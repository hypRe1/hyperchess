import { fail } from '@sveltejs/kit'
import type { Action, Actions } from './$types'

const login: Action = async ({ cookies, request }) => {
    const data = await request.formData()
    const username = data.get('username')
    const password = data.get('password')

    const response = await fetch("http://127.0.0.1:8000/api/user/token", {
        method: "POST",
        body: `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
    });

    const asJson = await response.json();

    if (!response.ok || response.body == null) {
        return fail(response.status, { error: true, detail: asJson.detail })
    }

    const token = asJson.access_token;
    cookies.set('token', token, {
        path: '/',
        httpOnly: true,
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production',
        maxAge: 7 * 24 * 60 * 60,
    })

    return { success: true }
}

export const actions: Actions = { default: login }
