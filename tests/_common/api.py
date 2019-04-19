import pytest


class CommonApiGet:
    def test_returns_json(self, client, route):
        resp = client.get(route, follow_redirects=True)
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'application/json'
