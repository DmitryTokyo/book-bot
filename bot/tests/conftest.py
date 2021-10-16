import pytest

from bot.app import app


@pytest.fixture
def client():
    app.config.from_object('config.config.TestingConfig')
    with app.test_client() as client:
        yield client
