import pytest

from src_api.endpoint import Games


@pytest.fixture
def known_games():
    """These are some games that are known to exist"""
    return [
        "o1y9okr6",
        "3dxy5vv6",
    ]


@pytest.mark.asyncio
async def test_get_known_games(src_api, known_games):
    for game_id in known_games:
        game = await src_api.query(Games).get(game_id)

        assert game.weblink != "", f"Known game {game_id} doesn't have a weblink!"
