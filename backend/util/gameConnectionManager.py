import random
import string

from chess import COLORS, Board, Color, IllegalMoveError, InvalidMoveError
from fastapi import WebSocket
from pydantic import BaseModel
from util.connectionManager import ConnectionManager
from util.matchModels import Match


class MatchListing(BaseModel):
    code: str
    public: bool
    creator: str
    colour: Color | None
    time: float
    bonus: int | None


class MatchListingRequestForm(BaseModel):
    public: bool
    colour: Color | None
    time: float
    bonus: int | None


class GameConnectionManager(ConnectionManager):
    def __init__(self):
        super().__init__()
        self.listing_listeners: set[str] = set()
        self.match_listeners: set[str] = set()
        self.public_listings: dict[str, MatchListing] = {}
        self.private_listings: dict[str, MatchListing] = {}
        self.public_matches: dict[str, Match] = {}
        self.private_matches: dict[str, Match] = {}
        self.creators: dict[str, str] = {}
        self.current_match: dict[str, str] = {}

    async def get_ws(self, username: str) -> WebSocket | None:
        ws = self.active_connections.get(username)
        if ws is None:
            await self.disconnect(username, None)
            return None
        return ws

    def get_match_from_code(self, code: str) -> Match | None:
        return self.public_matches.get(code) or self.private_matches.get(code)

    async def add_listing(
        self, form_data: MatchListingRequestForm, creator: str
    ) -> None:
        """
        Create a match listing
        """
        ws = await self.get_ws(creator)
        if ws is None:
            return

        if creator in self.creators:
            await ws.send_json(
                [
                    "addListing",
                    {
                        "success": False,
                        "detail": "You can only create one match listing at a time",
                    },
                ]
            )
            return

        code = "".join(random.choices(string.ascii_uppercase, k=4))

        match_listing = MatchListing(
            code=code,
            public=form_data.public,
            creator=creator,
            colour=form_data.colour,
            time=form_data.time,
            bonus=form_data.bonus,
        )

        self.creators[creator] = code
        if form_data.public:
            self.public_listings[code] = match_listing
            for listener in self.listing_listeners:
                listener_ws = await self.get_ws(listener)
                if listener_ws is not None:
                    await listener_ws.send_json(
                        [
                            "listenListings",
                            {"addListing": match_listing.model_dump()},
                        ]
                    )
        else:
            self.private_listings[code] = match_listing

        await ws.send_json(
            [
                "addListing",
                {"success": True, "listing": match_listing.model_dump()},
            ]
        )

    async def remove_listing(self, creator: str) -> None:
        """
        Delete a match listing that you have created
        """
        ws = await self.get_ws(creator)
        if ws is None:
            return
        code = self.creators.pop(creator, None)

        if self.public_listings.get(code) is not None:
            del self.public_listings[code]
            for listener in self.listing_listeners:
                listener_ws = await self.get_ws(listener)
                if listener_ws is not None:
                    await listener_ws.send_json(
                        [
                            "listenListings",
                            {"removeListing": code},
                        ]
                    )
        elif self.private_listings.get(code) is not None:
            del self.private_listings[code]
        else:
            await ws.send_json(
                [
                    "removeListing",
                    {
                        "success": False,
                        "detail": "You do not have a match listing to delete",
                    },
                ]
            )
            return

        await ws.send_json(
            [
                "removeListing",
                {
                    "success": True,
                    "code": code,
                },
            ]
        )

    async def accept_listing(self, code: str, opp: str):
        opp_ws = await self.get_ws(opp)
        if opp_ws is None:
            return

        listing = self.public_listings.pop(code, None) or self.public_listings.pop(
            code, None
        )

        if listing is None:
            await opp_ws.send_json(
                [
                    "addGame",
                    {
                        "success": False,
                        "code": "No match listing to create game from",
                    },
                ]
            )
            return

        creator_ws = await self.get_ws(listing.creator)

        if creator_ws is None:
            await opp_ws.send_json(
                [
                    "addGame",
                    {
                        "success": False,
                        "code": f"Player {listing.creator} disconnected",
                    },
                ]
            )
            return

        creator_colour = (
            random.choice(COLORS) if listing.colour is None else not listing.colour
        )

        if creator_colour:
            white = listing.creator
            black = opp
        else:
            white = opp
            black = listing.creator

        match = Match(
            code=code,
            public=listing.public,
            white_player=white,
            black_player=black,
            time=listing.time,
            bonus=listing.bonus,
            connected={listing.creator, opp},
            board=Board(),
        )

        if match.public:
            self.public_matches[code] = match
        else:
            self.private_matches[code] = match

        await opp_ws.send_json(["acceptListing", {"success": True}])

        for player in creator_ws, opp_ws:
            await player.send_json(["joinMatch", code])
            self.current_match[player] = code

    async def join_game(self, username: str, code: str):
        ws = await self.get_ws(username)
        if ws is None:
            return

        game = self.public_matches.get(code) or self.private_matches.get(code)

        if game is None:
            await ws.send_json(
                ["joinMatch", {"success": False, "detail": "Game does not exist"}]
            )
            return
        if game.game_over:
            await ws.send_json(
                ["joinMatch", {"success": False, "detail": "Game ended"}]
            )
            return

        game.connected.add(username)
        if game.public:
            self.public_matches[code] = game
        else:
            self.private_matches[code] = game
        await ws.send_json(
            [
                "joinMatch",
                game.to_match_model().model_dump(),
            ]
        )
        self.current_match[username] = code

    async def add_listing_listener(self, username: str):
        ws = await self.get_ws(username)
        if ws is None:
            return

        self.listing_listeners.add(username)
        await ws.send_json(
            [
                "listenListings",
                {
                    "success": True,
                    "listings": [
                        listing.model_dump()
                        for _, listing in self.public_listings.items()
                    ],
                },
            ]
        )

    async def add_match_listener(self, username: str):
        ws = await self.get_ws(username)
        if ws is None:
            return

        self.match_listeners.add(username)
        await ws.send_json(
            [
                "listenListings",
                {
                    "success": True,
                    "matches": [
                        match.to_match_model().model_dump()
                        for _, match in self.public_matches.items()
                    ],
                },
            ]
        )

    async def remove_listing_listener(self, username: str):
        ws = await self.get_ws(username)
        if ws is None:
            return

        if username not in self.listing_listeners:
            await ws.send_json(
                [
                    "listenListings",
                    {
                        "success": False,
                        "detail": "You are not already listening for listings",
                    },
                ]
            )
            return

        self.listing_listeners.add(username)
        await ws.send_json(["stoplistenListings", {"success": True}])

    async def remove_match_listener(self, username: str):
        ws = await self.get_ws(username)
        if ws is None:
            return

        if username not in self.listing_listeners:
            await ws.send_json(
                [
                    "listenMatches",
                    {
                        "success": False,
                        "detail": "You are not already listening for matches",
                    },
                ]
            )
            return

        self.listing_listeners.add(username)
        await ws.send_json(["stoplistenMatches", {"success": True}])

    async def make_move(self, username: str, move: str):
        ws = await self.get_ws(username)
        if ws is None:
            return

        if username not in self.current_match:
            await ws.send_json(
                [
                    "makeMove",
                    {
                        "success": False,
                        "detail": "You are not currently in a match",
                    },
                ]
            )
            return

        code = self.current_match[username]
        game = self.get_match_from_code(code)

        if game is None:
            await ws.send_json(
                [
                    "makeMove",
                    {
                        "success": False,
                        "detail": "Match does not exist",
                    },
                ]
            )
            return

        board = game.board

        print(username, game.to_match_model().model_dump())
        moving_player = game.white_player if board.turn else game.black_player
        if username != moving_player:
            await ws.send_json(
                [
                    "makeMove",
                    {
                        "success": False,
                        "detail": f"It is {moving_player}'s turn to move",
                    },
                ]
            )
            return

        try:
            print("pushing move")
            parsed_move = board.push_uci(move)
        except IllegalMoveError:
            await ws.send_json(
                [
                    "makeMove",
                    {
                        "success": False,
                        "detail": "Illegal move",
                    },
                ]
            )
        except InvalidMoveError:
            await ws.send_json(
                [
                    "makeMove",
                    {
                        "success": False,
                        "detail": "Invalid move",
                    },
                ]
            )
        else:
            game.board = board
            if game.public:
                self.public_matches[code] = game
            else:
                self.private_matches[code] = game

            for player in game.connected:
                if player == username:
                    await ws.send_json(["makeMove", {"success": True}])
                    continue

                player_ws = await self.get_ws(player)
                if player_ws is not None:
                    await player_ws.send_json(["pushMove", parsed_move.uci()])

    async def disconnect(self, username: str, ws: WebSocket | None):
        if username in self.active_connections and (
            (self.active_connections.get(username) == ws) or (ws is None)
        ):
            del self.active_connections[username]

        if username in self.creators:
            code = self.creators.pop(username)
            if self.public_listings.get(code) is not None:
                del self.public_listings[code]
                for listener in self.listing_listeners:
                    listener_ws = await self.get_ws(listener)
                    if listener_ws is not None:
                        await listener_ws.send_json(
                            [
                                "listenListings",
                                {"removeListing": code},
                            ]
                        )

            elif self.private_listings.get(code) is not None:
                del self.private_listings[code]
