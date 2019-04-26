import os
import pytest


@pytest.fixture
def client():
    from app.application import app
    app.config['TESTING'] = True
    client = app.test_client()
    yield client
