import type { LayoutServerLoad } from './$types'
import type { PersonalUserResponse } from "$lib/types/userTypes"


export const load: LayoutServerLoad = async ({ fetch, locals }) => {
    if (locals.loggedIn) {
        const profileResponse = await fetch("http://127.0.0.1:8000/api/user/profile", { method: "GET" })

        let profile: PersonalUserResponse = await profileResponse.json();

        return {
            loggedIn: true,
            profile: profile,
            dark: locals.appearance.dark,
            theme: locals.appearance.theme,
            countries: locals.countryData.countries
        }
    } else {
        return {
            loggedIn: false,
            dark: locals.appearance.dark,
            theme: locals.appearance.theme,
        }
    }
}
