import pytest

from speedrun_api.api import src_api
from speedrun_api.endpoint import Leaderboards


@pytest.fixture
def known_leaderboards():
    """These are some users that are known to exist"""
    return [
        ("o1y9okr6", "zd3xmmvd"),
        ("o1y9okr6", "vdo530yk"),
        ("3dxy5vv6", "wk6yjved"),
    ]


@pytest.mark.asyncio
async def test_get_known_leaderboards(known_leaderboards):
    for game_id, category_id in known_leaderboards:
        leaderboard = await (
            src_api.query(Leaderboards).where(game=game_id, category=category_id).all()
        )

        assert len(leaderboard.runs) > 0, "Known user did not return info"
