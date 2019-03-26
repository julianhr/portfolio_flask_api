import pytest


class CommonApiGet:
    def test_route_redirects(self, client, route):
        """ route redirects if it doesn't end with a slash """

        if (route.endswith('/')):
            pytest.skip()

        resp = client.get(route)
        assert resp.status_code == 308
        assert resp.location.endswith(route + '/')


    def test_returns_json(self, client, route):
        resp = client.get(route, follow_redirects=True)
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'application/json'
