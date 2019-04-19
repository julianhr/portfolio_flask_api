import pytest
import urllib
from tests._common.api import CommonApiGet


class TestIndex(CommonApiGet):
    @pytest.fixture
    def route(self):
        return '/labs/infinite-scroller'


    def test_json_shape(self, client, route):
        res = client.get(route, follow_redirects=True)
        entry = res.json[0]
        assert 'title' in entry
        assert 'image_url' in entry
        assert 'description' in entry


    def test_url_params(self, client, route):
        entries = 5
        paragraphs = 4
        query = dict(entries=entries, paragraphs=paragraphs)
        params = urllib.parse.urlencode(query)
        path = f'{route}?{params}'
        res = client.get(path, follow_redirects=True)
        json = res.json

        assert len(json) == entries
        assert len(json[0]['description']) == paragraphs
