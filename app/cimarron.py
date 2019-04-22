import os
from flask import Blueprint, jsonify, request, abort, Response, escape
from marshmallow import ValidationError
from itsdangerous import TimedJSONWebSignatureSerializer
import boto3

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
        errors = { k: l[0] for k, l in error.messages.items() }
        return jsonify({
            'error_type': 'ValidationError',
            'error_payload': errors
        }), 400
    except Exception as error:
        return jsonify({
            'error_type': 'generic',
            'error_payload': error,
        }), 400
