import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, cookies, params }) => {
    return {
        board: locals.appearance.board,
        piece: locals.appearance.piece,
        token: cookies.get("token"),
        code: params.code
    }
}
