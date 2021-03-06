import boto3
import os
from flask import Blueprint, jsonify, request, abort, Response, escape
from itsdangerous import TimedJSONWebSignatureSerializer
from marshmallow import ValidationError
from sentry_sdk import capture_exception

from utils import clamp_param_num
from utils.aws import ses_send_email_kwargs
from utils.cimarron_email import EmailSchema


EIGHT_HOURS = 60 * 60 * 8
bp = Blueprint('cimarron', __name__, url_prefix='/cimarron')
ses = boto3.client('ses')


@bp.route('/generate-token', methods=['GET'])
def generate_token():
    serializer = TimedJSONWebSignatureSerializer(
        os.environ['SECRET_KEY'],
        expires_in=EIGHT_HOURS
    )
    token = (
        serializer
            .dumps(os.environ['CSRF_PHRASE'])
            .decode('UTF-8')
    )
    return jsonify({ 'token': token })


@bp.route('/email', methods=['POST'])
def email():
    try:
        data = EmailSchema().load(request.get_json())
        kwargs = ses_send_email_kwargs(
            reply_to=escape(data['email']),
            email_to=os.environ['CONTACT_EMAIL_TO'],
            subject=escape(data['subject']),
            message=escape(data['message']),
        )
        ses.send_email(**kwargs)
        return '', 204
    except ValidationError as error:
        capture_exception(error)
        errors = { k: l[0] for k, l in error.messages.items() }
        return jsonify({
            'error_type': 'ValidationError',
            'error_payload': errors
        }), 400
    except Exception as error:
        capture_exception(error)
        return jsonify(
            error_type='generic',
            error_payload=str(error),
        ), 400
