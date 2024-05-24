import pytest

from speedrun_api.api import src_api
from speedrun_api.endpoint import Users


@pytest.fixture
def known_users():
    """These are some users that are known to exist"""
    return [
        "816w31rx",
        "8georwrj",
        "8e9k1yoj",
    ]


def test_get_username_for_known_users(known_users):
    for user_id in known_users:
        user = src_api.query(Users).get(user_id)

        assert user.name.lower() is not None, "Known user did not return info"


def test_get_personal_bests_for_known_users(known_users):
    for user_id in known_users:
        runs = src_api.query(Users.PersonalBests).where(user=user_id).all()
        assert len(runs) > 0, "Known user did not return personal bests"
