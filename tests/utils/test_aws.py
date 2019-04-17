import pytest


def test_ses_send_email(mocker):
    from utils.aws import ses, ses_send_email, _ses_send_email_kwargs
    mocker.patch.object(ses, 'send_email', return_value='this is a test')
    # args
    reply_to = ['reply@test.com']
    email_to = ['test@test.com']
    subject = 'test subject line'
    message = 'test message body'

    ses_send_email(reply_to, email_to, subject, message)

    ses.send_email.assert_called_with(
        **_ses_send_email_kwargs(reply_to, email_to, subject, message)
    )
