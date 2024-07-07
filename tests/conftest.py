import pytest
from src_api import SpeedrunApi


@pytest.fixture
def src_api():
    return SpeedrunApi()
