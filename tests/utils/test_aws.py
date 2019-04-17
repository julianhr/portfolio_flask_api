import pytest
import os


def test_ses_send_email(mocker, monkeypatch):
    from utils.aws import ses, ses_send_email, _ses_send_email_kwargs
    mocker.patch.object(ses, 'send_email', return_value='this is a test')
    # args
    reply_to = ['reply@test.com']
    email_to = ['test@test.com']
    subject = 'test subject line'
    message = 'test message body'

    monkeypatch.setattr(os, 'environ', dict(CONTACT_EMAIL_FROM='test@email.com'))
    print('\ntesting', os.environ['CONTACT_EMAIL_FROM'], end='\n')

    ses_send_email(reply_to, email_to, subject, message)

    ses.send_email.assert_called_with(
        **_ses_send_email_kwargs(reply_to, email_to, subject, message)
    )
