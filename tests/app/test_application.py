import re


class TestCorsPolicy:
    host_dev = 'http://localhost'
    host_prod = 'https://www.cimarron.me'


    def test_cors_dev_re(self, client):
        from app.application import cors_origin_dev_re
        assert bool(re.search(cors_origin_dev_re, self.host_dev))
        assert bool(re.search(cors_origin_dev_re, f'{self.host_dev}/'))
        assert bool(re.search(cors_origin_dev_re, f'{self.host_dev}:3015'))
        assert bool(re.search(cors_origin_dev_re, f'{self.host_dev}:3015/this/that'))

        assert bool(re.search(cors_origin_dev_re, 'https://localhost')) == False
        assert bool(re.search(cors_origin_dev_re, 'https://any')) == False


    def test_cors_prod_re(self, client):
        from app.application import cors_origin_prod_re
        assert bool(re.search(cors_origin_prod_re, self.host_prod))
        assert bool(re.search(cors_origin_prod_re, f'{self.host_prod}/'))
        assert bool(re.search(cors_origin_prod_re, f'{self.host_prod}/this/that'))
        assert bool(re.search(cors_origin_prod_re, f'{self.host_prod}/this/that/'))

        assert bool(re.search(cors_origin_prod_re, 'http://www.cimarron.me')) == False
        assert bool(re.search(cors_origin_prod_re, 'https://cimarron.me')) == False
        assert bool(re.search(cors_origin_prod_re, 'https://any.com')) == False


    def test_dev_request(self, client):
        res = client.get('/', headers={ 'Origin': self.host_dev })
        cors_header = 'Access-Control-Allow-Origin'
        assert res.headers.has_key(cors_header)
        assert res.headers[cors_header] == self.host_dev


def test_get_index(client):
    resp = client.get('/')
    json = resp.json
    assert resp.status_code == 200, 'should be 200'
    assert resp.headers['Content-Type'] == 'application/json'
    assert json['Output'] == 'Hello World'


def test_post_index(client):
    resp = client.post('/')
    data_json = resp.json
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'application/json'
    assert data_json['Output'] == 'Hello World'
