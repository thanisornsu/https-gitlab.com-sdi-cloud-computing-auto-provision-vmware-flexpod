# -*-coding: utf-8 -*-
# Import libraries
from flask import Flask, jsonify, request, Response, session
import requests
# JSON Library for return message
import json

import datetime
import time

# Import YAML Configuration
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# กำหนด File configuration path
CONFIG_FILE = 'Config.yml'
# โหลด Configuration จาก File config
try:
    file_stream = open(CONFIG_FILE, "r")
    # Load configuration into config
    config = load(file_stream, Loader=Loader)
except Exception as e:
    print("Read configuration file error:", e)
    exit(1)

# Define flask application
app = Flask(__name__)

# Add session secret key
app.secret_key = config['crypto']['secrete_key']


# Function: return JSON to client
def json_response(messages=None, status=None, headers=None):
    # Define default headers
    if headers == None:
        headers = dict()
    headers.update({"Content-Type": "application/json"})
    # Convert dict to json format
    contents = json.dumps(messages).replace('\'', '"')
    # Check return status code
    if (status == None):
        status = 200
    # Initialize response object
    resp = Response(response=contents, headers=headers, status=int(status))
    # Hide confidential sofware version by set to other value
    resp.headers['Server'] = config['server']['name']
    # Return response object
    return resp


def SendNotify(message='', sendto=''):
    RequestUrl = 'https://chat-public.one.th:8034/api/v1/push_message'
    RequestHeaders = {
        'Authorization': 'Bearer A31e127557d215875b9af0638989acc8e5b643c3162ea4ad3b2ed903b05b53c7003b4e78672594eeebda5529d09a2c55d',
        'Content-Type': 'application/json'
    }
    RequestData = {
        "to": sendto,
        "bot_id": config['notify']['botid'],
        "type": "text",
        "message": message
    }
    try:
        RequestResult = requests.post(url=RequestUrl, headers=RequestHeaders, data=json.dumps(RequestData), verify=False)
        return RequestResult.json()
    except Exception as e:
        msg = "Can't send message: %s" % e
        return msg

# Root Endpoint
# @app.route('/', methods=['GET'])
@app.route('/')
def RootEndpoint():
    # TODO: Test debug code here
    return json_response({"message": "Hello World"}, 200)


@app.route("/callback", methods=['POST'])
def callback():
    # get request body as text
    body = request.get_json(0)
    print(body)
    ### SEND USER/GROUP ID ###
    if 'sticker_id' in body['message']:
        if body['message']['sticker_id'] == 'Sef500528532e533c8551c27546fb32e1/Sef500528532e533c8551c27546fb32e1_8.png':
            if 'group_id' in body['source'].keys():
                msg = 'Your group id is %s' % body['source']['group_id']
                SendNotify(msg, body['source']['group_id'])
            else:
                msg = 'Your user id is %s' % body['source']['user_id']
                SendNotify(msg, body['source']['user_id'])
    # msg = '%s:%s' % (body['source']['user_id'], body['message']['text'])
    # response = SendNotify(msg, body['source']['user_id'])
    # print(response)
    return 'OK'


# Run Flask application
if __name__ == '__main__':

    # Open flask application
    try:
        app.run(debug=config['debug'], port=config['server']['port'], host=config['server']['host'])
        # line_bot_api.push_message(config['notify']['userid'], TextSendMessage(text='Start SO BOT'))
    except Exception as e:
        print("Cannot start Flask service daemon:", e)
        exit(1)