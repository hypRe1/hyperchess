import type { LayoutServerLoad } from './$types'
import type { PersonalUserResponse } from "$lib/types/userTypes"


export const load: LayoutServerLoad = async ({ fetch, locals }) => {
    if (locals.loggedIn) {
        const profileResponse = await fetch("http://127.0.0.1:8000/api/user/profile", { method: "GET" })

        let profile: PersonalUserResponse = await profileResponse.json();

        return {
            loggedIn: true,
            username: profile.username,
            about_me: profile.about_me,
            avatar: profile.avatar,
            dark: locals.appearance.dark,
            theme: locals.appearance.theme,
        }
    } else {
        return {
            loggedIn: false,
            dark: locals.appearance.dark,
            theme: locals.appearance.theme,
        }
    }
}
