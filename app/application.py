#!flask/bin/python
import json
from flask import Flask, jsonify
from flask_cors import CORS
from app.flaskrun import flaskrun


application = Flask(__name__)
app = application


# CORS
if app.config.get('ENV') == 'production':
    origin = '*'
else:
    origin = 'http://localhost:5000'

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
from .infinite_scroller import bp as infinite_scroll_bp
app.register_blueprint(infinite_scroll_bp)


if __name__ == '__main__':
    flaskrun(application)
