from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from util.gameConnectionManager import GameConnectionManager, MatchListingRequestForm

router = APIRouter(prefix="/match", tags=["match-listing"])
manager = GameConnectionManager()


@router.websocket("/ws")
async def match(websocket: WebSocket):
    """
    Match websocket
    """
    user = await manager.connect(websocket)
    if user is None:
        return
    try:
        while True:
            data = await websocket.receive_json()
            cmd = data[0]
            match cmd:
                case "addListing":
                    try:
                        form = MatchListingRequestForm.model_validate(data[1])
                    except ValidationError as e:
                        await manager.send_personal_message(
                            user.username,
                            ["addListing", {"success": False, "details": str(e)}],
                        )
                    await manager.add_listing(form, user.username)
                case "removeListing":
                    await manager.remove_listing(user.username)
                case "acceptListing":
                    await manager.accept_listing(data[1], user.username)

                case "listenListings":
                    await manager.add_listing_listener(user.username)
                case "listenMatches":
                    await manager.add_match_listener(user.username)
                case "stopListenListings":
                    await manager.remove_listing_listener(user.username)
                case "stopListenMatches":
                    await manager.remove_match_listener(user.username)

                case "joinMatch":
                    await manager.join_game(user.username, data[1])
                case "makeMove":
                    await manager.make_move(user.username, data[1])
                case "resign":
                    await manager.resign(user.username)
                case "draw":
                    await manager.draw(user.username, data[1])
                case "chat":
                    pass
                case "checkClock":
                    await manager.check_clock(user.username)
    except WebSocketDisconnect:
        await manager.disconnect(user.username, websocket)
