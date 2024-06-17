import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ fetch, locals }) => {
    if (locals.loggedIn) {
        const response = await fetch("http://127.0.0.1:8000/api/user/profile", {
            method: "GET",
            headers: {
                accept: 'application/json'
            }
        })

        let profile = await response.json();

        return {
            loggedIn: true,
            username: profile.username,
            about_me: profile.about_me,
            avatar: "data:image/png;base64, " + profile.avatar
        }
    } else {
        return {
            loggedIn: false,
        }
    }
}
