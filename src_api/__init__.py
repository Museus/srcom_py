import asyncio
import concurrent.futures
import functools
import logging
from typing import Any, Mapping, Optional, TypeVar

import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter, Retry


logger = logging.getLogger("SpeedrunApi")

EndpointType = TypeVar("EndpointType")


class SpeedrunApi:
    SITE_URL: str = "https://speedrun.com/api/v1"

    def __init__(self, api_key: str = None):
        session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=0.1,
        )

        session.mount("https://", HTTPAdapter(max_retries=retries))
        if api_key:
            session.headers["X-API-Key"] = api_key

        self.session = session

    def query(self, endpointType: EndpointType) -> EndpointType:
        return endpointType(self)

    async def _get(self, path: str, params: Optional[Mapping[str, Any]] = None):
        url = self.SITE_URL + path

        loop = asyncio.get_running_loop()
        try:
            with concurrent.futures.ProcessPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool,
                    functools.partial(
                        self.session.get,
                        url,
                        params=params,
                        timeout=10,
                    ),
                )
            response.raise_for_status()
        except HTTPError:
            logger.exception("[SpeedrunApi] GET failed!")
            raise

        return response.json()

    async def _post(self, path: str, data: Optional[Mapping[str, Any]]):
        url = self.SITE_URL + path

        loop = asyncio.get_running_loop()
        try:
            with concurrent.futures.ProcessPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool,
                    functools.partial(
                        self.session.get,
                        url,
                        json=data,
                        timeout=10,
                    ),
                )
            response.raise_for_status()
        except HTTPError:
            logger.exception("[SpeedrunApi] POST failed!")
            raise

        return response.json()
