from pydantic import BaseModel, OnErrorOmit

from .components import Category, Variable, User, PersonalBest, Leaderboard, Game, Run


class CategoryResponse(BaseModel):
    data: Category


class VariablesResponse(BaseModel):
    data: list[Variable]


class UsersResponse(BaseModel):
    data: User


class PersonalBestsResponse(BaseModel):
    data: list[OnErrorOmit[PersonalBest]]


class LeaderboardsResponse(BaseModel):
    data: Leaderboard


class GameResponse(BaseModel):
    data: Game


class RunsResponse(BaseModel):
    data: list[Run]
