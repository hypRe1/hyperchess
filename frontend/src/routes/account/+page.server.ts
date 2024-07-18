import type { PageServerLoad } from './$types';
import type { PersonalUserResponse, CountryResponse } from '$lib/types/userTypes';

export const load: PageServerLoad = async ({ fetch }) => {
    const profileResponse = await fetch("http://127.0.0.1:8000/api/user/profile", {
        method: "GET",
        headers: {
            accept: 'application/json'
        }
    })

    let userData: PersonalUserResponse = await profileResponse.json();
    userData.avatar = userData.avatar

    const countriesResponse = await fetch("http://127.0.0.1:8000/api/user/countries", {
        method: "GET",
        headers: {
            accept: 'application/json'
        }
    })

    let countriesData: CountryResponse = await countriesResponse.json()

    return {
        user: userData,
        countries: countriesData,
    };
}

export const ssr = false;