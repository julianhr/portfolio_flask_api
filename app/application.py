#!flask/bin/python
import json
from flask import Flask, jsonify
from flask_cors import CORS
from app.flaskrun import flaskrun


application = Flask(__name__)
app = application


# CORS
if app.config.get('ENV') == 'production':
    origin = r'https://(www\.cimarron\.me|.+unruffled-stallman-9cfd92\.netlify\.com)'
else:
    origin = r'http://localhost'

resources = {
    '*': {
        'origins': origin,
    }
}

CORS(app, origins=[origin])


# Test endpoints
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return jsonify({ 'Output': 'Hello World' })


# endpoint imports
from app.infinite_scroller import bp as infinite_scroll_bp
app.register_blueprint(infinite_scroll_bp)


if __name__ == '__main__':
    flaskrun(application)
