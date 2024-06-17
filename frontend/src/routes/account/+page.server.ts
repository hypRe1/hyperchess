import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
    const profileResponse = await fetch("http://127.0.0.1:8000/api/user/profile", {
        method: "GET",
        headers: {
            accept: 'application/json'
        }
    })

    interface profile {
        username: string;
        avatar: any;
        email: string;
        about_me: string | null;
        rating: number;
        country: string;
        registration_date: string;
    }

    let userData: profile = await profileResponse.json();
    userData.avatar = "data:image/png;base64, " + userData.avatar

    const countriesResponse = await fetch("http://127.0.0.1:8000/api/user/countries", {
        method: "GET",
        headers: {
            accept: 'application/json'
        }
    })

    interface country {
        name: string;
        emoji: string;
        image: string;
    }

    let countriesData: { [code: string]: country; } = await countriesResponse.json()

    return {
        user: userData,
        countries: countriesData,
    };
}

export const ssr = false;