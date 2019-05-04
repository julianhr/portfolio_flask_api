import re
import os
import sys
import pytest
import importlib


def test_is_production(monkeypatch, mocker):
    from app.application import is_production # make sys.modules aware of module
    mocker.patch('app.application.sentry_sdk.init')

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('APP_ENV', 'production')
    importlib.reload(sys.modules['app.application'])
    from app.application import is_production
    assert is_production

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('APP_ENV', 'development')
    importlib.reload(sys.modules['app.application'])
    from app.application import is_production
    assert not is_production

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('APP_ENV', 'testing')
    importlib.reload(sys.modules['app.application'])
    from app.application import is_production
    assert not is_production


class TestSentryInitialization:

    @pytest.fixture
    def set_env(self, monkeypatch, mocker):
        def fixture(app_env, sentry_dsn, is_testing):
            from app.application import is_production # make sys.modules aware of module
            monkeypatch.setenv('APP_ENV', app_env)
            monkeypatch.setenv('SENTRY_SDK_DSN', sentry_dsn)
            mocker.patch('app.application.sentry_sdk.init')
            importlib.reload(sys.modules['app.application'])

        return fixture


    def test_sentry_initialization_production(self, set_env):
        set_env('production', 'test_sentry_dsn', False)
        expected_args = dict(
            dsn='test_sentry_dsn',
            debug=False,
            environment='production',
            release='$Format:%h$',
        )

        from app.application import sentry_sdk
        _, kwargs = sentry_sdk.init.call_args
        args = { k: v for k, v in kwargs.items() if k in expected_args }
        assert sentry_sdk.init.called_once()
        assert args == expected_args


    def test_sentry_initialization_development(self, set_env):
        set_env('development', 'test_sentry_dsn', True)
        expected_args = dict(
            dsn=False,
            debug=True,
            environment='development',
        )

        from re import match as re_match
        from app.application import sentry_sdk
        _, kwargs = sentry_sdk.init.call_args
        args = { k: v for k, v in kwargs.items() if k in expected_args }
        assert sentry_sdk.init.called_once()
        assert args == expected_args
        assert bool(re_match(r'^[a-z0-9]{7}$', kwargs['release']))


class TestCorsPolicy:

    HOST_DEV = 'http://localhost'
    HOST_PROD = 'https://www.cimarron.me'


    def test_cors_dev_re(self):
        from app.application import cors_origin_dev_re
        assert bool(re.search(cors_origin_dev_re, self.HOST_DEV))
        assert bool(re.search(cors_origin_dev_re, f'{self.HOST_DEV}/'))
        assert bool(re.search(cors_origin_dev_re, f'{self.HOST_DEV}:3015'))
        assert bool(re.search(cors_origin_dev_re, f'{self.HOST_DEV}:3015/this/that'))

        assert bool(re.search(cors_origin_dev_re, 'https://localhost')) == False
        assert bool(re.search(cors_origin_dev_re, 'https://any')) == False


    def test_cors_prod_re(self):
        from app.application import cors_origin_prod_re
        assert bool(re.search(cors_origin_prod_re, self.HOST_PROD))
        assert bool(re.search(cors_origin_prod_re, f'{self.HOST_PROD}/'))
        assert bool(re.search(cors_origin_prod_re, f'{self.HOST_PROD}/this/that'))
        assert bool(re.search(cors_origin_prod_re, f'{self.HOST_PROD}/this/that/'))

        assert bool(re.search(cors_origin_prod_re, 'http://www.cimarron.me')) == False
        assert bool(re.search(cors_origin_prod_re, 'https://cimarron.me')) == False
        assert bool(re.search(cors_origin_prod_re, 'https://any.com')) == False


    def test_dev_request(self, get_client):
        client = get_client('development')
        res = client.get('/', headers={ 'Origin': self.HOST_DEV })
        cors_header = 'Access-Control-Allow-Origin'
        assert res.headers.has_key(cors_header)
        assert res.headers[cors_header] == self.HOST_DEV


    def test_prod_request(self, get_client, monkeypatch, mocker):
        client = get_client('production')
        res = client.get('/', headers={ 'Origin': self.HOST_PROD })
        cors_header = 'Access-Control-Allow-Origin'
        assert res.headers.has_key(cors_header)
        assert res.headers[cors_header] == self.HOST_PROD


def test_get_index(client):
    resp = client.get('/')
    json = resp.get_json()
    assert resp.status_code == 200, 'should be 200'
    assert resp.headers['Content-Type'] == 'application/json'
    assert json['Output'] == 'Hello World'


def test_post_index(client):
    resp = client.post('/')
    data_json = resp.get_json()
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'application/json'
    assert data_json['Output'] == 'Hello World'
