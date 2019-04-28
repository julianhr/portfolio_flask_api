#!flask/bin/python
import json
import logging
import os
import sentry_sdk
import subprocess
import watchtower
from flask import Flask, jsonify
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from app.flaskrun import flaskrun


is_production = os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('TESTING')


# initialize Sentry
git_hash = None

if is_production:
    with open(os.path.abspath('./version.txt')) as fh:
        git_hash = fh.readline().strip()
else:
    bstr_git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
    git_hash = str(bstr_git_hash.strip(), 'utf-8')

sentry_sdk.init(
    dsn=is_production and os.environ['SENTRY_SDK_DSN'],
    integrations=[FlaskIntegration()],
    release=git_hash,
    debug=(not is_production),
    environment=os.environ.get('FLASK_ENV'),
)


# setup app and env variables
app = Flask(__name__)
application = app

app.config.from_mapping(
    SECRET_KEY=os.environ['SECRET_KEY'],
    TESTING=os.environ.get('TESTING', False),
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
