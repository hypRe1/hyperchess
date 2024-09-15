import { fail } from '@sveltejs/kit'
import type { Action, Actions } from './$types'

// Handle login form submission
const login: Action = async ({ cookies, request }) => {
    // Retrieve form data from the request
    const data = await request.formData()
    const username = data.get('username')
    const password = data.get('password')

    // Make a POST request to the authentication API to get a token
    const response = await fetch("http://127.0.0.1:8000/api/user/token", {
        method: "POST",
        body: `grant_type=&username=${username}&password=${password}&scope=&client_id=&client_secret=`,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
    });

    // Parse the JSON response from the server
    const asJson = await response.json();

    // If the response is not ok or the body is null, return an error with details
    if (!response.ok || response.body == null) {
        return fail(response.status, { error: true, detail: asJson.detail })
    }

    // Extract the access token from the response
    const token = asJson.access_token;

    // Store the token in a cookie with secure settings
    cookies.set('token', token, {
        path: '/',  // Cookie is accessible site wide
        httpOnly: true,  // Cookie cannot be accessed by JavaScript (for security reasons)
        sameSite: 'strict',  // Ensures the cookie is sent only with same-site requests
        secure: process.env.NODE_ENV === 'production',  // Send cookie only over HTTPS in production
        maxAge: 7 * 24 * 60 * 60,  // Cookie expires after 7 days
    })

    return { success: true }
}

export const actions: Actions = { default: login }
