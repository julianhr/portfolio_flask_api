import os
import sys
import pytest
import importlib


# Pytest env variables
os.environ['APP_ENV'] = 'testing'


@pytest.fixture(scope='function')
def client(monkeypatch):
    from app.application import app
    client = app.test_client()
    return client


@pytest.fixture(scope='function')
def get_client(monkeypatch):
    def _client(env):
        monkeypatch.setenv('FLASK_ENV', env)
        monkeypatch.setenv('APP_ENV', env)
        importlib.reload(sys.modules['app.application'])
        from app.application import app
        client = app.test_client()
        return client

    return _client
