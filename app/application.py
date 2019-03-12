#!flask/bin/python
import json
from flask import Flask, Response
from app.flaskrun import flaskrun

application = Flask(__name__)
app = application

@app.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@app.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

if __name__ == '__main__':
    flaskrun(application)
