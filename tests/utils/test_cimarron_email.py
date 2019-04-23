import os
import pytest
import random
import time
from faker import Faker
from string import ascii_letters
from collections import namedtuple
from freezegun import freeze_time
from itsdangerous import TimedJSONWebSignatureSerializer
from marshmallow import ValidationError, pprint

from utils.cimarron_email import verify_token, EmailSchema


fake = Faker()

class TestVerifyToken:

    def setup_method(self):
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.patch('os.environ', return_value=dict(SECRET_KEY='testing_key'))

    @freeze_time('2019-11-11 00:00')
    def test_verifies_valid_token(self):
        expires_in = 60 * 10
        serializer = TimedJSONWebSignatureSerializer(
                    os.environ['SECRET_KEY'],
                    expires_in=expires_in
                )
        token = serializer.dumps('').decode('UTF-8')
        assert verify_token(token)


    @freeze_time('2019-11-11 00:00:10')
    def test_bad_signature(self):
        expires_in = 60 * 10
        serializer = TimedJSONWebSignatureSerializer(
                    os.environ['SECRET_KEY'],
                    expires_in=expires_in
                )
        token = serializer.dumps('some test text').decode('UTF-8')

        token_parts = token.split('.')
        signature = list(token_parts[2])
        i = random.randrange(0, len(signature))
        signature[i] = chr(ord(signature[i]) + 1)
        token_parts[2] = ''.join(signature)
        bad_token = ''.join(token_parts)

        assert verify_token(bad_token) is False


    def test_expired_token(self):
        token = None

        with freeze_time('2019-11-11 00:00'):
            ten_minutes = 60 * 10
            serializer = TimedJSONWebSignatureSerializer(
                        os.environ['SECRET_KEY'],
                        expires_in=ten_minutes
                    )
            token = serializer.dumps('some test text').decode('UTF-8')
            assert verify_token(token)

        with freeze_time('2019-11-11 00:09'):
            assert verify_token(token)

        with freeze_time('2019-11-11 00:10'):
            assert verify_token(token)

        with freeze_time('2019-11-11 00:11'):
            assert verify_token(token) is False

        with freeze_time('2019-11-11 00:12'):
            assert verify_token(token) is False


class TestEmailSchema:

    def csrf_token(self, datetime:str):
        ten_minutes = 60 * 10

        print('test time', datetime)
        with freeze_time(datetime):
            serializer = TimedJSONWebSignatureSerializer(
                os.environ['SECRET_KEY'],
                expires_in=ten_minutes
            )

            return serializer.dumps('testing text').decode('utf-8')


    def json_payload(self, datetime:str):
        return {
            'csrf_token': self.csrf_token(datetime),
            'email': 'julian@email.com',
            'name': 'Julian',
            'subject': 'test subject',
            'message': 'this is a long enough message that passes validation',
        }


    def test_all_fields_are_valid(self):
        datetime = '2019-11-11'

        with freeze_time(datetime):
            json = self.json_payload(datetime)
            assert EmailSchema().load(json)


    def test_csrf_token_is_invalid(self):
        datetime = '2019-11-11'
        json = self.json_payload(datetime)
        json['csrf_token'] = self.csrf_token(datetime)

        with freeze_time('2019-11-11 00:11'):
            with pytest.raises(ValidationError):
                EmailSchema().load(json)


    @freeze_time('2019-11-11')
    def test_email_validity(self):
        json = self.json_payload('2019-11-11')
        json['email'] = 'valid@somemail.com'
        assert EmailSchema().load(json)

        # invalid email
        with pytest.raises(ValidationError) as invalid:
            json['email'] = 'invalid@email'
            EmailSchema().load(json)
        assert invalid.value.messages['email'] == ['Not a valid email address.']

        # too short
        with pytest.raises(ValidationError) as invalid:
            json['email'] = 'a@o.com'
            EmailSchema().load(json)
        assert invalid.value.messages['email'] == ['Invalid value.']

        # too long
        with pytest.raises(ValidationError) as invalid:
            username = ''.join(random.choices(ascii_letters, k=40))
            json['email'] =  f'{username}@emails.com'
            EmailSchema().load(json)
        assert invalid.value.messages['email'] == ['Invalid value.']


    @freeze_time('2019-11-11')
    def test_name_validity(self):
        json = self.json_payload('2019-11-11')
        json['name'] = fake.name()
        assert EmailSchema().load(json)

        # too short
        with pytest.raises(ValidationError) as invalid:
            json['name'] = 'j'
            EmailSchema().load(json)
        assert invalid.value.messages['name'] == ['Invalid value.']

        # too long
        with pytest.raises(ValidationError) as invalid:
            max_len = 50
            fake_name = ''.join(random.choices(ascii_letters + ' ', k=max_len + 1))
            json['name'] = fake_name
            EmailSchema().load(json)
        assert invalid.value.messages['name'] == ['Invalid value.']


    @freeze_time('2019-11-11')
    def test_subject_validity(self):
        json = self.json_payload('2019-11-11')
        json['subject'] = 'Hello'
        assert EmailSchema().load(json)

        # too short
        with pytest.raises(ValidationError) as invalid:
            json['subject'] = 'j'
            EmailSchema().load(json)
        assert invalid.value.messages['subject'] == ['Invalid value.']

        # too long
        with pytest.raises(ValidationError) as invalid:
            max_len = 120
            fake_subject = ''.join(random.choices(ascii_letters + ' ', k=max_len + 1))
            json['subject'] = fake_subject
            EmailSchema().load(json)
        assert invalid.value.messages['subject'] == ['Invalid value.']


    @freeze_time('2019-11-11')
    def test_message_validity(self):
        json = self.json_payload('2019-11-11')
        json['message'] = fake.sentence(nb_words=100)
        assert EmailSchema().load(json)

        # too short
        with pytest.raises(ValidationError) as invalid:
            min_len = 50
            fake_message = ''.join(random.choices(ascii_letters + ' ', k=min_len - 1))
            json['message'] = 'j'
            EmailSchema().load(json)
        assert invalid.value.messages['message'] == ['Invalid value.']

        # too long
        with pytest.raises(ValidationError) as invalid:
            max_len = 10_000
            fake_message = ''.join(random.choices(ascii_letters + '     ', k=max_len + 1))
            json['message'] = fake_message
            EmailSchema().load(json)
        assert invalid.value.messages['message'] == ['Invalid value.']
