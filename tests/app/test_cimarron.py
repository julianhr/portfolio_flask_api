import pytest
import os
from flask import escape
from freezegun import freeze_time
from faker import Faker
from itsdangerous import TimedJSONWebSignatureSerializer


fake = Faker()

class TestGenerateToken:

    @pytest.fixture
    def route(self):
        return '/cimarron/generate-token'


    def test_json_shape(self, client, route):
        resp = client.get(route)
        json = resp.get_json()
        assert len(json) == 1
        assert 'token' in json


    def test_token_is_verifiable(self, client, route):
        from utils.cimarron_email import verify_token
        json = client.get(route).get_json()
        assert verify_token( json['token'] )


    def test_token_expires_in_eight_hours(self, client, route):
        from utils.cimarron_email import verify_token
        json = None

        with freeze_time('2019-11-11 00:00'):
            json = client.get(route).get_json()
            assert verify_token( json['token'] )

        with freeze_time('2019-11-11 07:59'):
            assert verify_token( json['token'] )

        with freeze_time('2019-11-11 08:00'):
            assert verify_token( json['token'] )

        with freeze_time('2019-11-11 08:01'):
            assert verify_token( json['token'] ) is False

        with freeze_time('2019-11-11 09:00'):
            assert verify_token( json['token'] ) is False


class TestEmail:

    TIME_FROZEN = '2019-11-11'
    SECRET_KEY = 'test_key'
    CONTACT_EMAIL_FROM = 'from@test.com'
    CONTACT_EMAIL_TO = 'to@test.com'

    def setup_method(self):
        from app.cimarron import ses
        from utils.aws import ses_send_email_kwargs
        from botocore.stub import Stubber
        self.ses = ses
        self.ses_send_email_kwargs = ses_send_email_kwargs
        self.Stubber = Stubber


    @pytest.fixture
    def mock_env(self, mocker):
        mock_return = dict(
            SECRET_KEY=TestEmail.SECRET_KEY,
            CONTACT_EMAIL_FROM=TestEmail.CONTACT_EMAIL_FROM,
            CONTACT_EMAIL_TO=TestEmail.CONTACT_EMAIL_TO,
        )
        mocker.patch('os.environ', new=mock_return)


    @pytest.fixture
    def csrf_token(self, mock_env):
        with freeze_time(TestEmail.TIME_FROZEN):
            expires_in = 60 * 10
            serializer = TimedJSONWebSignatureSerializer(
                            os.environ['SECRET_KEY'],
                            expires_in=expires_in
                        )
            return serializer.dumps('some test text').decode('UTF-8')


    @pytest.fixture
    def route(self):
        return '/cimarron/email'


    @pytest.fixture
    def data(self, client, csrf_token):
        return dict(
            csrf_token=csrf_token,
            email=TestEmail.CONTACT_EMAIL_FROM,
            name=fake.name(),
            subject=fake.sentence(nb_words=6),
            message=fake.sentence(nb_words=200),
        )


    def decorate_stubber(self, stubber, data):
        ses_resp = { 'MessageId': '1' }
        ses_kwargs = self.ses_send_email_kwargs(
            reply_to=data['email'],
            email_to=TestEmail.CONTACT_EMAIL_TO,
            subject=data['subject'],
            message=data['message'],
        )
        stubber.add_response('send_email', ses_resp, ses_kwargs)


    def test_successfully_sends_email(self, client, route, data):
        with self.Stubber(self.ses) as stubber:
            self.decorate_stubber(stubber, data)
            resp = client.post(route, json=data)
            assert resp.status_code == 204


    @freeze_time('2019-11-12') # 1 day after TIME_FROZEN
    def test_invalid_csrf_token(self, client, route, data):
        with self.Stubber(self.ses) as stubber:
            self.decorate_stubber(stubber, data)
            resp = client.post(route, json=data)
            json = resp.get_json()
            assert resp.status_code == 400
            assert json['error_type'] == 'ValidationError'
            assert 'error_payload' in json


    def test_user_text_is_escaped(self, client, route, csrf_token):
        with self.Stubber(self.ses) as stubber:
            json_raw = dict(
                csrf_token=csrf_token,
                email=TestEmail.CONTACT_EMAIL_FROM,
                name="<script>alert('very bad stuff')</script>",
                subject="<script>alert('very bad stuff')</script>",
                message="<script>alert('really really very bad stuff')</script>",
            )
            json_escaped = { k: escape(v) for k, v in json_raw.items() }

            self.decorate_stubber(stubber, json_escaped)
            resp = client.post(route, json=json_raw)
            assert resp.status_code == 204
