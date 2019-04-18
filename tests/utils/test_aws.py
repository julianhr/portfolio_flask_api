import pytest
import os

from utils.aws import ses_send_email_kwargs


class TestSesSendEmailKwargs:

    @pytest.fixture
    def kwargs(self):
        return dict(
            reply_to=['reply@test.com'],
            email_to=['test@test.com'],
            subject='test subject line',
            message='test message body',
        )

    
    @pytest.fixture
    def env(self, monkeypatch):
        env = dict(
            # SECRET_KEY='test_key',
            CONTACT_EMAIL_FROM='from@email.com',
            CONTACT_EMAIL_TO='to@email.com',
        )
        monkeypatch.setattr(os, 'environ', env)
        return env


    def test_source_key(self, kwargs, env):
        resp = ses_send_email_kwargs(**kwargs)
        assert resp['Source'] == env['CONTACT_EMAIL_FROM']


    def test_reply_to_address(self, kwargs):
        resp = ses_send_email_kwargs(**kwargs)
        assert resp['ReplyToAddresses'] == kwargs['reply_to']


    def test_destination(self, kwargs, env):
        resp = ses_send_email_kwargs(**kwargs)
        expected_json = {
            'ToAddresses': kwargs['email_to'],
        }
        assert resp['Destination'] == expected_json


    def test_message(self, kwargs, env):
        resp = ses_send_email_kwargs(**kwargs)
        expected_json = {
            'Subject': {
                'Data': kwargs['subject'],
                'Charset': 'UTF-8',
            },
            'Body': {
                'Text': {
                    'Data': kwargs['message'],
                    'Charset': 'UTF-8',
                },
                'Html': {
                    'Data': kwargs['message'],
                    'Charset': 'UTF-8',
                }
            }
        }
        assert resp['Message'] == expected_json
