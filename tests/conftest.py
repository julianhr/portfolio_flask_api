import os
import sys
import pytest
import importlib


# Pytest env variables
os.environ['TESTING'] = 'True'
os.environ['FLASK_ENV'] = 'production'


@pytest.fixture(scope='function')
def client(monkeypatch):
    from app.application import app
    client = app.test_client()
    return client


@pytest.fixture(scope='function')
def get_client(monkeypatch):
    def _client(env):
        monkeypatch.setenv('FLASK_ENV', env)
        importlib.reload(sys.modules['app.application'])
        from app.application import app
        client = app.test_client()
        return client

    return _client
