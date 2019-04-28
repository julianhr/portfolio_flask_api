import re
import os
import sys
import pytest
import importlib


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


    def test_dev_request(self, get_client, monkeypatch):
        client = get_client('development')
        res = client.get('/', headers={ 'Origin': self.HOST_DEV })
        cors_header = 'Access-Control-Allow-Origin'
        assert res.headers.has_key(cors_header)
        assert res.headers[cors_header] == self.HOST_DEV


    def test_prod_request(self, get_client, monkeypatch):
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
