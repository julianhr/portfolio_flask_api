#!flask/bin/python
import json
from flask import Flask, jsonify
from flask_cors import CORS
from app.flaskrun import flaskrun


app = Flask(__name__)
application = app


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
