# -*- coding: utf-8 -*
from ..helper.helper import json_response, check_parameter, check_parameter_table, encryptPass
from flask import request
from ..databases import User
from ..databases import db
# from ..regex import validator, user_pattern
from sqlalchemy.exc import IntegrityError
# import psycopg2
import uuid
import random
import time

sess = db.session


def getAllUserDB():
    global sess
    resp = []
    for user in sess.query(User):
        resp.append(user.response())
    return resp


def getUserData():
    data = getAllUserDB()
    # print data
    return json_response({"result": data}, 200)


def generateKeyUser():
    key = ""
    for i in range(random.randint(8, 15)):
        key += str(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=1234567890"))
    return key


def insertUser(username, password, role):
    global sess
    new_user = User(
        # id=int(uuid.uuid4()),
        # id=id,
        username=username,
        password=password,
        role=role,
        create_date=str(time.time()),
        # key_user=key_hash
    )
    sess.add(new_user)
    sess.commit()

# def checkPaternUsername(username):
#     if validator(username, user_pattern["username"]) and len(username) >= 6 and len(username) <= 20:
#         return True
#     else:
#         return False
#
#
# def checkPaternPassword(password):
#     if validator(password, user_pattern["password"]) and len(password) >= 8:
#         return True
#     else:
#         return False


def createUser():
    get_data = request.json
    missing_key = check_parameter(
        get_data.keys(), ["username", "password", "confirm_password", "role"])
    if missing_key != []:
        return json_response({"message": "Missing parameter: " + ",".join(missing_key)}, 400)
    if User.query.filter_by(username=get_data["username"]).first() != None:
        return json_response({"message": "This user already exists."}, 400)
    elif get_data["password"] != get_data["confirm_password"]:
        return json_response({"message": "Password and confirm not match."}, 400)
    # elif not checkPaternUsername(get_data["username"]):
    #     return json_response({"message": "Username pattern not match."}, 400)
    # elif not checkPaternPassword(get_data["password"]):
    #     return json_response({"message": "Password pattern not match."}, 400)
    else:
        key_hash = generateKeyUser()
        encrypt_password = encryptPass(
            get_data["username"],
            get_data["password"],
            # key_hash
        )
        insertUser(
            # get_data["user_id"],
            get_data["username"],
            encrypt_password,
            get_data["role"],
            # key_hash
        )
        return json_response({"message": "Add user success"}, 200)
