from string import Template
from typing import TypeVar, TYPE_CHECKING

import pydantic

from . import schemas

if TYPE_CHECKING:
    from api import SpeedrunApi

SchemaT = TypeVar("SchemaT", bound=pydantic.BaseModel)
EndpointT = TypeVar("EndpointT", bound="Endpoint")
EmbeddableEndpointT = TypeVar("EmbeddableEndpointT", bound="EmbeddableEndpoint")


class PaginationMixin:
    offset: int

    def offset(self, entries: int):
        self.offset = entries


class Endpoint:
    _path: str
    params: dict[str, str | int]
    src_api: "SpeedrunApi"

    response_schema: SchemaT
    params_schema: SchemaT

    validate: bool = True
    unwrap: bool = True

    @property
    def path(self) -> str:
        return self._path

    def __init__(self: EndpointT, api_instance: "SpeedrunApi") -> EndpointT:
        self.api = api_instance
        self.params = {}

    def options(
        self: EndpointT, *, validate: bool = None, unwrap: bool = None
    ) -> EndpointT:
        if validate is not None:
            self.validate = validate
        if unwrap is not None:
            self.unwrap = unwrap

        return self

    def where(self: EndpointT, **parameters) -> EndpointT:
        parsed_parameters: pydantic.BaseModel = self.params_schema(**parameters)

        self.params.update(
            {
                parameter: getattr(parsed_parameters, parameter)
                for parameter in parsed_parameters.model_fields_set
            }
        )

        return self

    async def get(self, resource_id: str) -> SchemaT:
        """Get a specific resource by ID"""
        response = await self.api._get(self.path + "/" + resource_id)

        if not self.validate:
            return response if not self.unwrap else response.get("data", {})

        validated = self.response_schema(**response)

        return validated.data if self.unwrap else validated

    async def all(self) -> list[SchemaT]:
        response = await self.api._get(self.path)

        if not self.validate:
            return response if not self.unwrap else response.get("data", {})

        validated = self.response_schema(**response)

        return validated.data if self.unwrap else validated


class EmbeddableEndpoint(Endpoint):
    can_embed: list[str]

    def __init__(self: EmbeddableEndpointT, api_instance) -> EmbeddableEndpointT:
        super().__init__(api_instance)
        self.embedded = []

    def embed(self: EmbeddableEndpointT, *args) -> EmbeddableEndpointT:
        for arg in args:
            if arg not in self.can_embed:
                raise ValueError(f"Cannot embed {arg} in {type(self)}")

        embedded = {e for e in self.params.get("embed", "").split(",") if e}
        embedded.update(args)
        self.params["embed"] = list(embedded)

        return self


class Users(EmbeddableEndpoint):
    _path = "/users"
    response_schema = schemas.responses.UsersResponse
    params_schema = schemas.params.Users

    class PersonalBests(EmbeddableEndpoint):
        _path = "/users"
        response_schema = schemas.responses.PersonalBestsResponse
        params_schema = schemas.params.PersonalBests

        target_user = ""

        @property
        def path(self):
            return self._path + "/" + self.target_user + "/personal-bests"

        def where(self: EndpointT, *, user: str = "", **kwargs) -> EndpointT:
            if user:
                self.target_user = user

            super().where(**kwargs)

            return self


class Leaderboards(Endpoint):
    _path = "/leaderboards"
    response_schema = schemas.responses.LeaderboardsResponse
    params_schema = schemas.params.Leaderboards

    target_game: str
    target_category: str

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
        self: EndpointT,
        *,
        game: str = None,
        category: str = None,
        **params: dict[str, str],
    ) -> EndpointT:
        self.target_game = game
        self.target_category = category

        super().where(**params)

        return self

    @property
    def path(self):
        url_template = Template("${path}/${game}/category/${category}")

        return url_template.substitute(
            path=self._path, game=self.target_game, category=self.target_category
        )


class Games(Endpoint):
    _path = "/games"
    response_schema = schemas.responses.GameResponse
    params_schema = schemas.params.Games

    class Variables(Endpoint):
        response_schema = schemas.responses.VariablesResponse
        params_schema = schemas.params.Runs

        @property
        def path(self):
            return f"/games/{self.target_game}/variables"

        def where(self: EndpointT, *, game_id: str = "", **kwargs) -> EndpointT:
            if game_id:
                self.target_game = game_id

            super().where(**kwargs)

            return self


class Runs(EmbeddableEndpoint, PaginationMixin):
    _path = "/runs"
    response_schema = schemas.responses.RunsResponse
    params_schema = schemas.params.Runs

    can_embed = [
        "game",
        "category",
        "level",
        "players",
        "region",
        "platform",
        "variables",
    ]
