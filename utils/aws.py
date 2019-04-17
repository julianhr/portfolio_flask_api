import os
import boto3
from typing import List


ses = boto3.client('ses')


# surround in a try/catch
def ses_send_email(reply_to: List, email_to: List, subject: str, message: str) -> None:
    ses.send_email(
        **_ses_send_email_kwargs(reply_to, email_to, subject, message)
    )


def _ses_send_email_kwargs(reply_to, email_to, subject, message):
    return dict(
        Source=os.environ['CONTACT_EMAIL_FROM'],
        ReplyToAddresses=reply_to,
        Destination={
            'ToAddresses': email_to,
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8',
            },
            'Body': {
                'Text': {
                    'Data': message,
                    'Charset': 'UTF-8',
                },
                'Html': {
                    'Data': message,
                    'Charset': 'UTF-8',
                }
            }
        },
    )
