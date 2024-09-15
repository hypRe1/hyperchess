import { redirect } from '@sveltejs/kit'
import type { PageServerLoad } from './$types'

// Handle logout logic on page load
export const load: PageServerLoad = async ({ cookies }) => {
    // Remove token cookie using old expiration data
    cookies.set('token', '', {
        path: '/',
        expires: new Date(0),
    })

    // Redirect the user to the login page
    redirect(302, '/login')
}
