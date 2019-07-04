from flask import Response, json, request
import json
from functools import wraps
from ..databases import User, db
import hashlib


def json_response(messages=None, status=None, headers=None):
    if headers == None:
        headers = dict()
    headers.update({"Content-Type": "application/json"})
    contents = json.dumps(messages).replace('\'', '"')
    if(status == None):
        status = 200
    resp = Response(response=contents, headers=headers, status=int(status))
    return resp


def check_parameter(data, key):
    missing_key = []
    for k in key:
        if k not in data:
            missing_key.append(k)
    return missing_key


def check_parameter_table(data, table, extension_key=None):
    key = [col.name for col in table.__table__.columns if not col.nullable and not col.primary_key or (
        col.unique and not col.nullable)]
    if extension_key != None:
        for k in extension_key:
            key.append(k)
    print key
    missing_key = []
    is_valid = True
    print data
    for k in key:
        if k not in data:
            missing_key.append(k)
            is_valid = False
    return missing_key


def check_ticket(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return json_response({"message": "test decorator"})
    return decorated_function


############################# LOGIN ##############################
# def encryptPass(username, password, key_in_hash):
#     encrypt_user_pass = hashlib.sha1(username+'&'+password).hexdigest()
#     encrypt = encrypt_user_pass+key_in_hash
#     for i in range(10):
#         encrypt = hashlib.sha256(encrypt).hexdigest()
#     return encrypt


def encryptPass(username, password):
    encrypt_user_pass = hashlib.sha1(username+'&'+password).hexdigest()
    encrypt = encrypt_user_pass
    for i in range(10):
        encrypt = hashlib.sha256(encrypt).hexdigest()
    return encrypt


def apiLogin():
    get_data = request.json
    get_data_user = User.query.filter_by(username=get_data["username"]).first()
    if get_data_user != None:
        user = get_data_user.response()
        encrypt_password = encryptPass(
            get_data["username"],
            get_data["password"],
            user["key_user"]
        )
        if encrypt_password == user["password"]:
            return json_response({
                "message": "Login success",
                "access_token": True,
                "refresh_token": True,
                "token_type": "admin"
            }, 200)
        else:
            return json_response({"message": "Invalid password."}, 400)
    else:
        return json_response({"message": "Not found this username."}, 400)
