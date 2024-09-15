import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, cookies, params }) => {
    return {
        appearance: locals.appearance,
        token: cookies.get("token"),
        code: params.code
    }
}
