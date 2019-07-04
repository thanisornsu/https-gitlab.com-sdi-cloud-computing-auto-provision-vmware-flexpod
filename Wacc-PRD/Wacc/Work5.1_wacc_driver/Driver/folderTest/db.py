from flaskext.mysql import MySQL
from flask import Flask, request, jsonify, current_app, abort, send_from_directory
from functools import wraps
from flask_cors import CORS, cross_origin

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'sdi'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'test_sdi'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)


def connect_sql():
    def wrap(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Setup connection
                connection = mysql.connect()
                cursor = connection.cursor()
                return_val = fn(cursor, *args, **kwargs)
            finally:
                # Close connection
                connection.commit()
                connection.close()
            return return_val
        return wrapper
    return wrap


def fetchAlltoJson(data,columns):
    results = []
    for row in data:
        results.append(dict(zip(columns, row)))
    return results


def fetchOnetoJson(data,columns):
    result =  dict(zip(columns, data))
    return result
