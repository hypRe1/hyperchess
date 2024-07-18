export async function load(event) {
    return { "token": event.cookies.get("token") }
}
