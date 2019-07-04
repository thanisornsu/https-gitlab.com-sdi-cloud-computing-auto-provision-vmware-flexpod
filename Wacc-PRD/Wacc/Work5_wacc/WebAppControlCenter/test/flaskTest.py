from flask import Flask, Response, json, request, abort, make_response, jsonify
import requests
import json


app = Flask(__name__)


def json_response(messages=None, status=None, headers=None):
    if headers == None:
        headers = dict()
    headers.update({"Content-Type": "application/json"})
    contents = json.dumps(messages)
    if contents[0] == '\'' and contents[len(contents)] == '\'':
        contents.replace('\'', '"')
    if status == None:
        status = 200
    resp = Response(response=contents, headers=headers, status=int(status))

    return resp


@app.route('/test/post', methods=['POST'])
def create_task():
    data = request.get_json()
    # print data
    return json_response({"message": data}, 202)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')