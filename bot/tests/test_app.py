import pytest


def test_check(client):
    response = client.get('/')

    assert response == 200
