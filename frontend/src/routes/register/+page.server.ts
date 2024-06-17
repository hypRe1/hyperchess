import { fail } from '@sveltejs/kit'
import type { Action, Actions } from './$types'

const register: Action = async ({ cookies, request }) => {
    const data = await request.formData()
    const username = data.get('username')
    const email = data.get('email')
    const password = data.get('password')
    const confirm_password = data.get("confirm password")

    if (password != confirm_password) {
        return fail(400, { error: true, detail: "Passwords not matching" })
    }

    const response = await fetch("http://127.0.0.1:8000/api/user/", {
        method: "POST",
        body: `username=${username}&email=${email}&password=${password}`,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
    });

    const asJson = await response.json();

    if (!response.ok || response.body == null) {
        return fail(response.status, { error: true, detail: asJson.detail })
    }

    const loginResponse = await fetch("http://127.0.0.1:8000/api/user/token", {
        method: "POST",
        body: `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
    });

    const loginAsJson = await loginResponse.json();

    if (!loginResponse.ok || loginResponse.body == null) {
        return fail(loginResponse.status, { error: true, detail: loginAsJson.detail })
    }

    const token = loginAsJson.access_token;
    cookies.set('token', token, {
        path: '/',
        httpOnly: true,
        sameSite: 'strict',
        secure: process.env.NODE_ENV === 'production',
        maxAge: 20 * 60,
    })

    return { success: true }
}

export const actions: Actions = { default: register }
