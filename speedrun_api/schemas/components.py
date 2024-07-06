from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, OnErrorOmit


class Names(BaseModel):
    international: str
    japanese: Optional[str] = None


class Color(BaseModel):
    light: str
    dark: str


class GradientNameStyle(BaseModel):
    style: Literal["gradient"]
    color_from: Color = Field(..., alias="color-from")
    color_to: Color = Field(..., alias="color-to")


class SolidNameStyle(BaseModel):
    style: Literal["solid"]
    color: Color


class Country(BaseModel):
    code: str
    names: Names


class Region(BaseModel):
    code: str
    names: Names


class Location(BaseModel):
    country: Optional[Country] = None
    region: Optional[Region] = None


class Social(BaseModel):
    uri: str


class Asset(BaseModel):
    uri: Optional[str] = None


class Assets(BaseModel):
    icon: Asset
    supporterIcon: Optional[Asset] = None
    image: Asset


class GameNames(BaseModel):
    international: str
    japanese: Optional[str]
    twitch: Optional[str]


class Ruleset(BaseModel):
    show_milliseconds: bool = Field(..., alias="show-milliseconds")
    require_verification: bool = Field(..., alias="require-verification")
    require_video: bool = Field(..., alias="require-video")
    run_times: list[str] = Field(..., alias="run-times")
    default_time: str = Field(..., alias="default-time")
    emulators_allowed: bool = Field(..., alias="emulators-allowed")


class GameAssets(BaseModel):
    logo: Optional[Asset] = None
    cover_tiny: Optional[Asset] = Field(None, alias="cover-tiny")
    cover_small: Optional[Asset] = Field(None, alias="cover-small")
    cover_medium: Optional[Asset] = Field(None, alias="cover-medium")
    cover_large: Optional[Asset] = Field(None, alias="cover-large")
    icon: Optional[Asset] = None
    trophy_1st: Optional[Asset] = Field(None, alias="trophy-1st")
    trophy_2nd: Optional[Asset] = Field(None, alias="trophy-2nd")
    trophy_3rd: Optional[Asset] = Field(None, alias="trophy-3rd")
    trophy_4th: Optional[Asset] = Field(None, alias="trophy-4th")
    background: Optional[Asset] = None
    foreground: Optional[Asset] = None


class Link(BaseModel):
    rel: str
    uri: str


class Game(BaseModel):
    id: str
    names: GameNames
    boostReceived: int
    boostDistinctDonors: int
    abbreviation: str
    weblink: str
    discord: str
    released: int
    release_date: str = Field(..., alias="release-date")
    ruleset: Ruleset
    romhack: bool
    gametypes: list
    platforms: list[str]
    regions: list
    genres: list[str]
    engines: list
    developers: list[str]
    publishers: list[str]
    moderators: dict[str, str]
    created: str
    assets: GameAssets
    links: list[Link]


class RegisteredPlayer(BaseModel):
    rel: Literal["user"]
    id: str
    uri: str


class GuestPlayer(BaseModel):
    rel: Literal["guest"]
    name: str
    uri: str


class Scope(BaseModel):
    type: str


class VariableName(BaseModel):
    label: str


class Flags(BaseModel):
    miscellaneous: str


class Flags6(BaseModel):
    miscellaneous: bool


class VariableValueValues(BaseModel):
    label: str
    rules: Optional[str] = None


class VariableValues(BaseModel):
    field_note: str = Field(..., alias="_note")
    # choices: Optional[dict[str, str]] = None
    values: dict[str, VariableValueValues]
    default: Optional[str] = None


class Variable(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    scope: Scope
    mandatory: bool
    user_defined: bool = Field(..., alias="user-defined")
    obsoletes: bool
    values: VariableValues
    is_subcategory: bool = Field(..., alias="is-subcategory")
    links: list[Link]


class Category(BaseModel):
    id: str
    name: str
    weblink: str
    type: str
    rules: str
    players: list[Union[RegisteredPlayer, GuestPlayer]]
    miscellaneous: bool
    links: list[Link]


class Videos(BaseModel):
    text: Optional[str] = None
    links: Optional[list[Asset]] = None


class VerifiedStatus(BaseModel):
    status: Literal["verified"]
    examiner: Optional[str] = None
    verify_date: Optional[str] = Field(None, alias="verify-date")


class RejectedStatus(BaseModel):
    status: Literal["rejected"]
    examiner: str


class PendingStatus(BaseModel):
    status: Literal["pending"]


class Times(BaseModel):
    primary: str
    primary_t: float
    realtime: Optional[str] = None
    realtime_t: Optional[float] = None
    realtime_noloads: Optional[str] = None
    realtime_noloads_t: Optional[float] = None
    ingame: Optional[str] = None
    ingame_t: Optional[float] = None


class System(BaseModel):
    platform: Optional[str] = None
    emulated: bool
    region: Optional[str] = None


class Reference(BaseModel):
    uri: str
    rel: str


class Run(BaseModel):
    id: str
    weblink: str
    game: str
    level: Optional[str] = None
    category: str
    videos: Optional[Videos] = None
    comment: Optional[str] = None
    status: VerifiedStatus | RejectedStatus | PendingStatus = Field(
        ..., discriminator="status"
    )
    players: list[Union[RegisteredPlayer, GuestPlayer]]
    date: Optional[str] = None
    submitted: Optional[str] = None
    times: Times
    system: System
    splits: Optional[Reference] = None
    values: Optional[dict[str, str]] = None
    links: Optional[list[Reference]] = None


class User(BaseModel):
    id: str
    names: Names
    supporterAnimation: bool
    pronouns: Optional[str] = None
    weblink: str
    name_style: Union[GradientNameStyle, SolidNameStyle] = Field(
        ..., alias="name-style", discriminator="style"
    )
    role: str
    signup: datetime
    location: Optional[Location] = None
    twitch: Optional[Social] = None
    hitbox: Optional[Social] = None
    youtube: Optional[Social] = None
    twitter: Optional[Social] = None
    speedrunslive: Optional[Social] = None
    assets: Assets
    links: list[Link]

    @property
    def name(self) -> str:
        return self.names.international or "unknown"


class PersonalBest(BaseModel):
    place: int
    run: "Run"


class LeaderboardEntry(BaseModel):
    place: int
    run: Run


class Leaderboard(BaseModel):
    weblink: str
    game: str
    category: str
    level: Optional[str] = None
    platform: Optional[str] = None
    region: Optional[str] = None
    emulators: Optional[str] = None
    video_only: bool = Field(..., alias="video-only")
    timing: str
    runs: list[OnErrorOmit[LeaderboardEntry]]
    links: list[Reference]
