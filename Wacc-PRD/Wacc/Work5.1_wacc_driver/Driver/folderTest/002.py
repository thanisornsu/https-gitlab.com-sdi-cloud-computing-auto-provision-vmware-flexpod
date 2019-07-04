import subprocess, yaml, threading
# from db import *
from flask import Flask, request, jsonify

app = Flask(__name__)
# CORS(app)


@app.route("/api/v1/users",methods=['POST'])
@connect_sql()
def user_post(cursor):  # Camel case
    data = request.json
    query = "UPDATE `user` SET `user`= '%s',`password`= '%s',`token`= '%s' WHERE `user`= '%s'" % (data['username'], data['password'], data['token'],data['username'])  # Method Post should be Create(Insert)
    try:
        cursor.execute(query)
        obj = {"status" : "success"}
        return jsonify(obj)
    except:
        obj = { "status" : "fail" }
        return jsonify(obj)
    finally:
        cursor.close()


@app.route("/api/v1/users",methods=['GET'])
@connect_sql()
def user_get(cursor):  # Camel case
    data = request.json
    query = "SELECT * FROM `user` WHERE `user` = '%s' AND `password` = '%s'" % (data['username'], data['password'])
    cursor.execute(query)
    result = cursor.fetchone()
    if result is not None:
        columns = [column[0] for column in cursor.description]
        jsonResult = fetchOnetoJson(result, columns)
        obj = {"status": "success", "info": jsonResult}
        return jsonify(obj)
    else:
        obj = {"status": "fail"}
        return jsonify(obj)
    cursor.close()


@app.route("/api/v1/users",methods=['PUT'])
@connect_sql()
def user_put(cursor):  # Camel case
    data = request.json
    query = "INSERT INTO `user`(`user`, `password`) VALUES ('%s','%s')" %(data['username'],data['password'])  # Method Put should be Update(Update)
    try:
        cursor.execute(query)
        obj = {"status": "success"}
        return jsonify(obj)
    except:
        obj = {"status": "fail"}
        return jsonify(obj)
    finally:
        cursor.close()


@app.route("/api/v1/users",methods=['DELETE'])
@connect_sql()
def user_delete(cursor):  # Camel case
    data = request.json
    query = "DELETE FROM `user` WHERE `user` = '%s' AND `password` = '%s'" % (data['username'], data['password'])
    try:
        cursor.execute(query)
        obj = {"status": "success"}
        return jsonify(obj)
    except:
        obj = {"status": "fail"}
        return jsonify(obj)
    finally:
        cursor.close()


@app.route("/api/v1/ping/yaml/", methods=['POST'])
def pingYaml():
    with open("config.yaml", "r") as f:
        tmp = yaml.load(f)
        resul_tdic = {}
        resul_tdic['result'] = {}
        threads = []
        for i in range(len(tmp['network']['address'])):
            process = threading.Thread(target=pingIP, args=(resul_tdic, tmp['network']['address'][i]))
            process.start()
            threads.append(process)
        for process in threads:
            process.join()
        f.close()
    resp = jsonify(resul_tdic)
    resp.status_code = 200
    return (resp)


def pingIP(result_dic, ip_address):
    proc = subprocess.Popen(
        ['ping', ip_address],
        stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        response = stdout.decode('ASCII')
        result_dic['result'][ip_address] = str(
            response[response.find("Average = ") + 10: response[response.find("Average = ")].find("ms") - 1])
    else:
        result_dic['result'][ip_address] = "ping fail"


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,threaded=True)