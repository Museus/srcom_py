from string import Template
from typing import TYPE_CHECKING

from pydantic import BaseModel

from . import schemas

if TYPE_CHECKING:
    from api import SpeedrunApi


class Endpoint:
    path: str
    schema: BaseModel
    src_api: "SpeedrunApi"

    validate: bool = True
    unwrap: bool = True

    def __init__(self, api_instance):
        self.api = api_instance
        self.params = {}

    def options(self, *, validate: bool = None, unwrap: bool = None):
        if validate is not None:
            self.validate = validate
        if unwrap is not None:
            self.unwrap = unwrap

        return self

    def get(self, resource_id: str):
        """Get a specific resource by ID"""
        response = self.api._get(self.path + "/" + resource_id, unwrap=self.unwrap)
        if not self.validate:
            return response

        return self.schema(**response)

    def all(self):
        response = self.api._get(self.path, unwrap=self.unwrap)
        if not self.validate:
            return response

        return [self.schema(**entry) for entry in self.api._get(self.path)]


class EmbeddableEndpoint(Endpoint):
    can_embed: list[str]

    embedded: list[str]

    def __init__(self, api_instance):
        super().__init__(api_instance)
        self.embedded = []

    def embed(self, *args):
        for arg in args:
            if arg not in self.can_embed:
                raise ValueError(f"Cannot embed {arg} in {type(self)}")

        self.embedded = args

        return self


class Users(EmbeddableEndpoint):
    path = "/users"
    schema = schemas.User

    class PersonalBests(EmbeddableEndpoint):
        path = "/users"
        accepted_params = ["top", "series", "game"]
        can_embed = ["game", "category", "level", "players", "region", "platform"]

        target_user = ""

        def where(
            self, *, user: str, top: int = None, series: str = None, game: str = None
        ):
            """Get personal bests for a user, optionally filtered by top X runs, game series, or specific game.
            https://github.com/speedruncomorg/api/blob/master/version1/users.md#get-usersidpersonal-bests

            Args:
                user_id (str): _description_
                top (int, optional): _description_. Defaults to None.
                series (str, optional): _description_. Defaults to None.
                game (str, optional): _description_. Defaults to None.
            """
            self.target_user = user

            params = dict(self.params)

            if top is not None:
                params["top"] = top
            if series is not None:
                params["series"] = series
            if game is not None:
                params["game"] = game

            self.params = params

            return self

        def all(self):
            response = self.api._get(
                self.path + "/" + self.target_user + "/personal-bests",
                params=self.params,
                unwrap=self.unwrap,
            )

            if not self.validate:
                return response

            return [schemas.PersonalBest(**run) for run in response]


class Leaderboards(Endpoint):
    path = "/leaderboards"
    schema = schemas.Leaderboard

    target_game: str
    target_category: str

    accepted_params = [
        "top",
        "platform",
        "region",
        "emulators",
        "video-only",
        "timing",
        "date",
        "var-",
    ]

    can_embed = [
        "game",
        "category",
        "level",
        "players",
        "regions",
        "platforms",
        "variables",
    ]

    def where(
        self,
        *,
        game: str,
        category: str,
        top: int = None,
        platform: str = None,
        region: str = None,
        emulators: list[str] = None,
        video_only: bool = None,
        timing: str = None,
        date: str = None,
        **vars: dict[str, str],
    ):
        self.target_game = game
        self.target_category = category

        params = dict(self.params)
        if top is not None:
            params["top"] = top
        if platform is not None:
            params["platform"] = platform
        if region is not None:
            params["region"] = region
        if emulators is not None:
            params["emulators"] = emulators
        if video_only is not None:
            params["video-only"] = video_only
        if timing is not None:
            params["timing"] = timing
        if date is not None:
            params["date"] = date
        for var_id, var_value in vars.items():
            params[f"var-{var_id}"] = var_value

        self.params = params

        return self

    def all(self):
        url_template = Template("${path}/${game}/category/${category}")
        response = self.api._get(
            url_template.substitute(
                path=self.path, game=self.target_game, category=self.target_category
            ),
            params=self.params,
            unwrap=self.unwrap,
        )

        if not self.validate:
            return self.response

        return self.schema(**response)


class Games(Endpoint):
    path = "/games"
    schema = schemas.Game

    class Variables(Endpoint):
        path = "/games/${game_id}/variables"
        schema = schemas.Variable

        def where(self, *, game_id: str = ""):
            url_template = Template(self.path)

            response = self.api._get(
                url_template.substitute(game_id=game_id),
                params=self.params,
                unwrap=self.unwrap,
            )

            if not self.validate:
                return response

            return [self.schema(**variable) for variable in response]


class Runs(EmbeddableEndpoint):
    path = "/runs"
    schema = schemas.Run

    target_game = None
    can_embed = ["game", "category", "level", "players", "region", "platform"]

    def where(
        self,
        *,
        game: str = None,
        status: str = None,
        orderby: str = None,
        max: int = None,
        direction: str = None,
        offset: int = None,
    ):
        params = dict(self.params)

        if game is not None:
            params["game"] = game
        if status is not None:
            params["status"] = status
        if orderby is not None:
            params["orderby"] = orderby
        if max is not None:
            params["max"] = max
        if direction is not None:
            params["direction"] = direction
        self.params = params

        return self

    def all(self):
        response = self.api._get(self.path, params=self.params, unwrap=self.unwrap)
        if not self.validate:
            return response

        return [self.schema(**run) for run in response]
