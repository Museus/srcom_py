from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class AcceptsVariables:
    """Mixin for routes that accept Variables as parameters. Provide the
    variables as {id: value} pairs, and the model will automatically convert
    them to {var-<id>: value} fields, to be used in requests.
    """

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def set_variable_columns(cls, data: dict[str, Any]):
        if isinstance(data, dict):
            extra_fields = data.keys() - cls.model_fields.keys()
            for field_name in extra_fields:
                if len(field_name) == 8 and field_name.isalnum():
                    data[f"var-{field_name}"] = data.pop(field_name)

        return data


class OrderBy(BaseModel):
    pass


class Orderable(BaseModel):
    direction: Optional[Literal["asc"] | Literal["desc"]] = None
    orderby: Optional[OrderBy] = None


class Users(BaseModel):
    # when given, searches the value (case-insensitive exact-string match) across user names, URLs and social profiles
    # all other query string filters are disabled when this is given
    lookup: Optional[str] = None

    # only returns users whose name/URL contains the given value; the comparision is case-insensitive
    name: Optional[str] = None

    # searches for Twitch usernames
    twitch: Optional[str] = None

    # searches for Hitbox usernames
    hitbox: Optional[str] = None

    # searches for Twitter usernames
    twitter: Optional[str] = None

    # searches for SpeedRunsLive usernames
    speedrunslive: Optional[str] = None


class PersonalBests(BaseModel):
    top: Optional[int] = None
    series: Optional[str] = None
    game: Optional[str] = None


class Leaderboards(BaseModel, AcceptsVariables):
    game: Optional[str] = None
    category: Optional[str] = None
    top: Optional[int] = None
    platform: Optional[str] = None
    region: Optional[str] = None
    emulators: Optional[list[str]] = None
    video_only: Optional[bool] = None
    timing: Optional[str] = None
    date: Optional[str] = None


class Games(BaseModel):
    pass


class Runs(BaseModel, AcceptsVariables):
    pass
