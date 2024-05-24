import datetime
import logging
import re
from typing import Any, Iterator, Mapping, Optional

import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter, Retry

from . import endpoint, schemas

logger = logging.getLogger("SpeedrunApi")


class SpeedrunApi:
    SITE_URL: str = "https://speedrun.com/api/v1"

    def __init__(self):
        session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=0.1,
        )

        session.mount("https://", HTTPAdapter(max_retries=retries))

        self.session = session

    def query(self, endpointType) -> endpoint.Endpoint:
        return endpointType(self)

    def _get(
        self, path: str, params: Optional[Mapping[str, Any]] = None, unwrap: bool = True
    ):
        url = self.SITE_URL + path

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
        except HTTPError:
            logger.exception("[SpeedrunApi] GET failed!")
            raise

        parsed_response: dict = response.json()
        if not unwrap:
            return parsed_response

        return parsed_response.get("data", parsed_response)

    def _post(self, path: str, data: Optional[Mapping[str, Any]], unwrap: bool = True):
        url = self.SITE_URL + path

        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
        except HTTPError:
            logger.exception("[SpeedrunApi] POST failed!")
            raise

        parsed_response: dict = response.json()
        if not unwrap:
            return parsed_response

        return parsed_response.get("data", parsed_response)

    def get_leaderboard(
        self,
        game: str,
        category: str,
        subcategories: Mapping[str, str] = None,
        as_of: datetime.datetime = None,
    ):
        query = self.query(endpoint.Leaderboards)
        query = query.where(game=game, category=category, **subcategories)

        if as_of:
            query.where(date=as_of.isoformat())

        leaderboard = query.all()

        return leaderboard.runs

    def get_game_icon_url(self, game):
        game_data = self.query(endpoint.Games).get(game)

        return game_data["assets"]["icon"]["uri"]

    def get_latest_run(self, game: str):
        runs = (
            self.query(endpoint.Runs)
            .where(
                game=game,
                status="verified",
                orderby="verify-date",
                direction="desc",
                max=1,
            )
            .embed("game", "category", "variables", "players", "level")
            .all()
        )
        return schemas.Run(**runs[0])

    def get_verified_runs(
        self, game: str, since: datetime.datetime | None
    ) -> Iterator[schemas.Run]:
        query = (
            self.query(endpoint.Runs)
            .where(
                game=game,
                status="verified",
                orderby="verify-date",
                max=200,
                direction="desc" if since else "asc",
            )
            .embed("game", "category", "players", "level")
            .options(validate=False, unwrap=False)
        )

        response = query.all()

        full_list = []
        should_break = False

        while True:
            for run in response["data"]:
                if (not since) or (
                    datetime.datetime.fromisoformat(
                        run["status"]["verify-date"] + "+00:00"
                    ).replace(tzinfo=datetime.timezone.utc)
                    > since
                ):
                    full_list.append(schemas.Run(**run))
                else:
                    should_break = True
                    break

            if should_break:
                break

            for link in response["pagination"]["links"]:
                if link["rel"] == "next":
                    url = link["uri"]
                    try:
                        offset = re.search(r"offset=(\d+)", url).group(1)
                        print(url)
                        print(offset)
                    except Exception:
                        offset = 0

            query = query.where(offset=offset)

            response = query.all()

        for run in reversed(full_list):
            yield run

    def get_game_variables(self, game: str) -> dict[str, Any]:
        path = f"/games/{game}/variables"

        try:
            return self._get(path)
        except Exception:
            return {}


src_api = SpeedrunApi()
