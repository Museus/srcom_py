from typing import TYPE_CHECKING

import pytest

from speedrun_api.api import src_api
from speedrun_api.endpoint import Users

if TYPE_CHECKING:
    from speedrun_api import schemas


@pytest.fixture
def known_users():
    """These are some users that are known to exist"""
    return [
        "816w31rx",
        "8georwrj",
        "8e9k1yoj",
    ]


@pytest.mark.asyncio
async def test_get_username_for_known_users(known_users):
    for user_id in known_users:
        user: "schemas.User" = await src_api.query(Users).get(user_id)

        assert user.name.lower() is not None, "Known user did not return info"


@pytest.mark.asyncio
async def test_get_personal_bests_for_known_users(known_users):
    for user_id in known_users:
        runs: list[schemas.Run] = (
            await src_api.query(Users.PersonalBests).where(user=user_id).all()
        )
        assert len(runs) > 0, "Known user did not return personal bests"
