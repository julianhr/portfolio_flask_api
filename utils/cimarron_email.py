import os
from marshmallow import Schema, fields, validates, ValidationError, pprint
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired


def verify_token(token):
    serializer = TimedJSONWebSignatureSerializer(os.environ['SECRET_KEY'])

    try:
        serializer.loads(token)
        return True
    except (BadSignature, SignatureExpired):
        return False


class EmailSchema(Schema):
    csrf_token = fields.String(
        required=True,
        validate=verify_token,
    )
    email = fields.Email(
        required=True,
        validate=lambda v: 8 <= len(v) <= 50,
    )
    name = fields.String(
        required=True,
        validate=lambda v: 2 <= len(v) <= 50,
    )
    subject = fields.String(
        required=True,
        validate=lambda v: 2 <= len(v) <= 120,
    )
    message = fields.String(
        required=True,
        validate=lambda v: 50 <= len(v) <= 10_000,
    )
