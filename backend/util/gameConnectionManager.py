import datetime
import random
import string
import time

from chess import COLORS, Color, IllegalMoveError, InvalidMoveError
from database import get_db
from fastapi import WebSocket
from models import Matches, UserMatches
from pydantic import BaseModel
from util.connectionManager import ConnectionManager
from util.gameCompressor import compress
from util.matchModels import Match, Result


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
    """
    Manages the WebSocket connections and game logic.
    This class handles game listings, game matches, and player interactions
    """

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
        """
        Get WebSocket connection from username
        """
        ws = self.active_connections.get(username)
        if ws is None:
            await self.disconnect(username, None)
            return None
        return ws

    def get_match_from_code(self, code: str) -> Match | None:
        """
        Get match object from code
        """
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

        if form_data.time == 0 and form_data.bonus == 0:
            await ws.send_json(
                [
                    "addListing",
                    {
                        "success": False,
                        "detail": "You cannot create a match with no time",
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
        Delete a match listing given creator's username
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
        """
        Accept a match listing
        """
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

        game = self.get_match_from_code(code)

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
        """
        Notify user when listings are created
        """
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
        """
        Notify user when matches are started
        """
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
        """
        Remove users' listing notifier
        """
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
        """
        Remove a user's match notifier
        """
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
        """
        Make a move if in a match
        """
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
                ["makeMove", {"success": False, "detail": "Game does not exist"}]
            )
            return
        if game.game_over:
            await ws.send_json(["makeMove", {"success": False, "detail": "Game ended"}])
            return

        moving_player = game.white_player if game.board.turn else game.black_player
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
            parsed_move = game.board.push_uci(move)
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
            time_spent = time.time() - game.time_started - sum(game.timings)
            game.timings.append(time_spent)
            time_left = (
                game.time * 60
                + game.bonus
                - sum(
                    [
                        game.timings[i] - game.bonus
                        for i in range(int(not game.board.turn), len(game.timings), 2)
                    ]
                )
            )

            if time_left < 0:
                game.game_over = True
                game.winner = not game.board.turn
                game.result = Result.FLAGGED

            if game.board.is_checkmate():
                game.game_over = True
                game.winner = not game.board.turn
                game.result = Result.CHECKMATE

            elif game.board.is_stalemate():
                game.game_over = True
                game.winner = None
                game.result = Result.STALEMATE

            elif game.board.is_insufficient_material():
                game.game_over = True
                game.winner = None
                game.result = Result.INSUFFICIENT_MATERIAL

            elif game.board.is_repetition():
                game.game_over = True
                game.winner = None
                game.result = Result.REPETITION

            elif game.board.is_seventyfive_moves():
                game.game_over = True
                game.winner = None
                game.result = Result.SEVENTYFIVE_MOVES

            if game.public:
                self.public_matches[code] = game
            else:
                self.private_matches[code] = game

            uci_move = parsed_move.uci()
            for player in game.connected:
                if player == username:
                    await ws.send_json(
                        ["makeMove", {"success": True, "time": time_spent}]
                    )
                    if game.game_over:
                        await ws.send_json(
                            ["gameOver", {"result": game.result, "winner": game.winner}]
                        )
                    continue

                player_ws = await self.get_ws(player)
                if player_ws is not None:
                    await player_ws.send_json(
                        ["pushMove", {"move": uci_move, "time": time_spent}]
                    )
                    if game.game_over:
                        await player_ws.send_json(
                            ["gameOver", {"result": game.result, "winner": game.winner}]
                        )

            if game.game_over:
                await self.archive_match(code)

    async def check_clock(self, username: str):
        """
        Check whether game should be over yet
        Called when player has been timed-out client-side
        """
        ws = await self.get_ws(username)
        if ws is None:
            return

        if username not in self.current_match:
            await ws.send_json(
                [
                    "checkClock",
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
                    "checkClock",
                    {
                        "success": False,
                        "detail": "Game does not exist",
                    },
                ]
            )
            return

        if game.game_over:
            await ws.send_json(
                [
                    "checkClock",
                    {
                        "success": False,
                        "detail": "Game is already over",
                    },
                ]
            )
            return

        time_spent = time.time() - game.time_started - sum(game.timings)
        time_left = (
            game.time * 60
            + game.bonus
            - sum(
                [
                    game.timings[i] - game.bonus
                    for i in range(int(not game.board.turn), len(game.timings), 2)
                ]
            )
            - time_spent
        )

        if time_left <= 0:
            game.game_over = True
            game.winner = not game.board.turn
            game.result = Result.FLAGGED
            if game.public:
                self.public_matches[code] = game
            else:
                self.private_matches[code] = game
            for player in game.connected:
                player_ws = await self.get_ws(player)
                if player_ws is not None:
                    await player_ws.send_json(
                        ["gameOver", {"result": game.result, "winner": game.winner}]
                    )

            await self.archive_match(code)

        await ws.send_json(["checkClock", {"success": True, "time_left": time_left}])

    async def resign(self, username: str):
        """
        User resigns match
        """
        ws = await self.get_ws(username)
        if ws is None:
            return

        if username not in self.current_match:
            await ws.send_json(
                [
                    "resign",
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
                ["resign", {"success": False, "detail": "Game does not exist"}]
            )
            return
        if game.game_over:
            await ws.send_json(["resign", {"success": False, "detail": "Game ended"}])
            return

        game.game_over = True
        game.result = Result.RESIGN
        if username == game.white_player:
            game.winner = False
        elif username == game.black_player:
            game.winner = True
        else:
            await ws.send_json(
                [
                    "resign",
                    {"success": False, "detail": "You are not playing in this match"},
                ]
            )
            return

        for player in game.connected:
            if player == username:
                await ws.send_json(["resign", {"success": True}])
                await ws.send_json(
                    ["gameOver", {"result": game.result, "winner": game.winner}]
                )
                continue

            player_ws = await self.get_ws(player)
            if player_ws is not None:
                await player_ws.send_json(
                    ["gameOver", {"result": game.result, "winner": game.winner}]
                )

        await self.archive_match(code)

    async def draw(self, username: str, type: str):
        """
        Method for all draw related messages

        Possible types:
        offer - player offers draw
        accept - player accepts draw offer
        decline - player declines draw offer
        disable - player disables draws entirely (to stop player from spamming draw offers)
        """
        ws = await self.get_ws(username)
        if ws is None:
            return

        if username not in self.current_match:
            await ws.send_json(
                [
                    "draw",
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
                ["draw", {"success": False, "detail": "Game does not exist"}]
            )
            return
        if game.game_over:
            await ws.send_json(["draw", {"success": False, "detail": "Game ended"}])
            return

        if username != game.white_player and username != game.black_player:
            await ws.send_json(
                [
                    "draw",
                    {"success": False, "detail": "You are not playing in this match"},
                ]
            )
            return

        if game.draw_disabled:
            await ws.send_json(["draw", "error", "Draw offers have been disabled"])
            return

        match type:
            case "offer":
                if game.draw_offer is not None:
                    await ws.send_json(
                        ["draw", "error", "There is already an ongoing draw offer"]
                    )
                    return
                game.draw_offer = username == game.white_player
                opponent_ws = await self.get_ws(
                    game.black_player if game.draw_offer else game.white_player
                )
                await opponent_ws.send_json(["draw", "offer"])
                await ws.send_json(["draw", "sent"])
            case "accept":
                if (username == game.black_player) and game.draw_offer:
                    game.game_over = True
                    game.result = Result.AGREEMENT
                    game.winner = None

                    for player in game.connected:
                        if player == username:
                            await ws.send_json(["draw", {"success": True}])
                            await ws.send_json(
                                [
                                    "gameOver",
                                    {"result": game.result, "winner": game.winner},
                                ]
                            )
                            continue

                        player_ws = await self.get_ws(player)
                        if player_ws is not None:
                            await player_ws.send_json(
                                [
                                    "gameOver",
                                    {"result": game.result, "winner": game.winner},
                                ]
                            )

            case "decline":
                opponent_ws = await self.get_ws(
                    game.white_player if game.draw_offer else game.black_player
                )
                await opponent_ws.send_json(["draw", "decline"])
                game.draw_offer = None

            case "disable":
                game.draw_disabled = True

            case _:
                await ws.send_json(["draw", "error", "Invalid draw type"])
                return

        if game.public:
            self.public_matches[code] = game
        else:
            self.private_matches[code] = game

        if game.game_over:
            await self.archive_match(code)

    async def archive_match(self, code):
        match = self.get_match_from_code(code)
        if match is None:
            raise ValueError
        if not match.game_over:
            raise ValueError

        moves_compressed = compress(match.board.move_stack)
        match_id = random.randint(0, 2000000000)

        create_match_model = Matches(
            id=match_id,
            white=match.white_player,
            black=match.black_player,
            moves=moves_compressed,
            winner=match.winner,
            result=match.result,
            time=match.time,
            bonus=match.bonus,
            time_started=datetime.datetime.fromtimestamp(match.time_started),
            hyperchess=True,
        )

        async for db in get_db():
            db.add(create_match_model)
            db.add(UserMatches(username=match.white_player, matchId=match_id))
            db.add(UserMatches(username=match.black_player, matchId=match_id))

            try:
                await db.commit()
            except Exception as e:
                print(e)

    async def disconnect(self, username: str, ws: WebSocket | None):
        """
        Disconnects a user's WebSocket connection
        Overrides parent disconnect method with extra functionality when a user is disconnected
        Removes match listings made by user that is disconnected
        """

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
