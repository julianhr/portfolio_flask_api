#!flask/bin/python
import os
import json
import logging
import watchtower
import sentry_sdk
import subprocess
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, jsonify
from flask_cors import CORS

from app.flaskrun import flaskrun


# initialize Sentry
git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
is_sentry_enabled = os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('TESTING')
sentry_sdk.init(
    dsn=os.environ['SENTRY_SDK_DSN'] if is_sentry_enabled else None,
    integrations=[FlaskIntegration()],
    release=git_hash,
    debug=os.environ.get('FLASK_ENV') != 'production',
    environment=os.environ.get('FLASK_ENV'),
)


# setup app and env variables
app = Flask(__name__)
application = app

app.config.from_mapping(
    SECRET_KEY=os.environ['SECRET_KEY'],
    TESTING=os.environ.get('TESTING'),
)


# logging
logging.basicConfig(level=logging.INFO)
log = app.logger

# adds watchtower handle only if AWS credentials found
# prevents tests from failing during CI build
try:
    wh = watchtower.CloudWatchLogHandler()
    app.logger.addHandler(wh)
    logging.getLogger("werkzeug").addHandler(wh)
except:
    pass


# CORS
cors_origin_prod_re = r'https://(www\.cimarron\.me|.+unruffled-stallman-9cfd92\.netlify\.com)'
cors_origin_dev_re = r'http://localhost.?'

if app.config.get('ENV') == 'production':
    origin = cors_origin_prod_re
else:
    origin = cors_origin_dev_re

resources = {
    '*': {
        'origins': origin,
    }
}

cors = CORS(app, origins=[origin])


# Test endpoints
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return jsonify({ 'Output': 'Hello World' })


# endpoint imports
from app.labs.infinite_scroller import bp as infinite_scroller_bp
app.register_blueprint(infinite_scroller_bp)

from app.cimarron import bp as cimarron_bp
app.register_blueprint(cimarron_bp)


if __name__ == '__main__':
    flaskrun(app)
