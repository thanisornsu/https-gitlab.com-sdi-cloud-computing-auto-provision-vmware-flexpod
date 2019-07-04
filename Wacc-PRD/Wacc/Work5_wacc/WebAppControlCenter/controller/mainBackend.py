from flask import Flask, Response, json, request, abort, make_response, jsonify
import requests
import urllib3
from ..databases import db, Network
import time
from yaml import load
import threading
from multiprocessing.pool import ThreadPool

from ..driver.main import sendData, detailData, storageData, createMainVolume, aggregateValue, vServerName, volumeName

urllib3.disable_warnings()

sess = db.session

network_config = load(open("WebAppControlCenter\controller\\network_config.yaml"))


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


def checkParameter(data, key):
    missing_key = []
    is_valid = True
    for k in key:
        if k not in data:
            missing_key.append(k)
            is_valid = False
    return is_valid, missing_key


def getAllNetworkDB():
    global sess
    resp = []
    for user in sess.query(Network):
        resp.append(user.response())
    return resp


def insertNetworkIp(network_ip, network_type):
    global sess
    new_network = Network(
        network_ip=network_ip,
        network_type=network_type,
        create_date=str(time.time()),
    )
    sess.add(new_network)
    sess.commit()


# ----------------------------------------------------- Provisioning ---------------------------------------------------


def getData():
    send_url = "http://127.0.0.1:5002/api/v1/vm"
    return_data = requests.request("GET", send_url)
    return_data = json.loads(return_data.text)
    if type(return_data) is unicode:
        return json_response({"message": return_data}, 200)
    return json_response({"result": return_data}, 200)


def getStorage():
    body_data = request.get_json()
    headers = request.headers
    print headers

    send_url = "http://127.0.0.1:5002/api/v1/vm/storage"
    # send_url = "http://172.16.39.154:5555/api/v1/vcloud/get_org"
    return_data = requests.request("GET", send_url)
    return_data = json.loads(return_data.text)
    return json_response({"result": return_data}, 200)


def getOrg():
    send_url = "http://127.0.0.1:5002/api/v1/vm/org"
    # send_url = "http://172.16.39.154:5555/api/v1/vcloud/get_org"
    return_data = requests.request("GET", send_url)
    return_data = json.loads(return_data.text)
    return json_response({"result": return_data}, 200)


def getVdc(org_name):
    send_url = "http://127.0.0.1:5002/api/v1/vm/org/{}".format(org_name)
    # send_url = "http://172.16.39.154:5555/api/v1/vcloud/get_org"
    return_data = requests.request("GET", send_url)
    return_data = json.loads(return_data.text)
    return json_response({"result": return_data}, 200)


def getVapp(org_name, vdc_name):
    send_url = "http://127.0.0.1:5002/api/v1/vm/org/{}/{}".format(org_name, vdc_name)
    # send_url = "http://172.16.39.154:5555/api/v1/vcloud/get_org"
    return_data = requests.request("GET", send_url)
    return_data = json.loads(return_data.text)
    return json_response({"result": return_data}, 200)


def provisioning(body_data):
    send_url = "http://127.0.0.1:5002/api/v1/vm"
    # body_data = request.get_json()
    headers = {
        "platform": "flexpod"
    }
    # data = {
    #     # data that i want
    #     "name": "L_vm",
    #     "storage": "datastore-12",
    #     "storageType": "thin",
    #     "templateId": "04d9ed8b-03d1-4e31-934b-ca8962de63ff",
    #     "templateName": "Fortigate",
    #     # "template_name": "Template_Windows2012_prd_api",
    #     "networkId": "Don't know",
    #     "networkName": "VXLAN-DVUplinks-25 or dvportgroup-26",
    #     "username": "mai dai tum wai",
    #     "customerName": "L_cust_test",
    #     "orgName": "L_org_test",
    #     "vdcName": "L_vdc_test",
    #     "vAppName": "L_vapp_test",
    #     "vAppUser": "L_vapp_user",
    #     "vAppPassword": "L_vapp_pass",
    #     "vAppPasswordConfirm": "L_vapp_pass",
    #     "zone": "POC"
    # }
    # body_data = data
    # checking_key, missing_key = checkParameter(body_data.keys(), ["name", "storage", "storageType", "templateId",
    #                                                               "templateName", "networkId", "networkName",
    #                                                               "customerName])
    # if checking_key:
    #     pass
    # else:
    #     return json_response({"message": "Missing parameters: " + ",".join(missing_key)}, 400)

    # data = {
    #     # data that i want
    #     "name": "L_SampleVM",
    #     "serviceOs": "WINDOWS_8_64",
    #     "datastore": "datastore-11",
    #     "folder": "group-v3",
    #     "resourcePool": "resgroup-21",
    #     "memorySize": "4 GB",
    #     "cpuCount": "2 Core",
    #     "diskCapacity": "20 GB",
    #     "networkType": "E1000",
    #     "backingType": "STANDARD_PORTGROUP",
    #     "network": "network-13",
    #     "customerName": "L_cust_test",
    #     "orgName": "L_org_test",
    #     "vdcName": "L_vdc_test",
    #     "vAppName": "L_vapp_test",
    #     "vAppUser": "L_vapp_user",
    #     "vAppPassword": "L_vapp_pass",
    #     "vAppPasswordConfirm": "L_vapp_pass",
    #     "zone": "POC"
    # }
    # body_data = data
    # checking_key, missing_key = checkParameter(body_data.keys(), ["name", "serviceOs", "datastore", "folder",
    #                                                               "resourcePool", "memorySize", "cpuCount",
    #                                                               "diskCapacity", "networkType", "backingType",
    #                                                               "network", "customerName"])
    # if checking_key:
    #     pass
    # else:
    #     return json_response({"message": "Missing parameters: " + ",".join(missing_key)}, 400)

    # body_data = request.get_json()

    # vm_name = body_data["name"]

    vapp_password = body_data["vAppPassword"]
    vapp_password_confirm = body_data["vAppPasswordConfirm"]

    if vapp_password != vapp_password_confirm:
        return "Vapp password doesn't match"

    # return_result, return_data = sendData(body_data)
    return_data = requests.request("POST", send_url, json=body_data, headers=headers)
    return_data = json.loads(return_data.text)
    status_code = return_data["statusCode"]
    del return_data["statusCode"]
    # return json_response({"message": "Your vm name {} has been deploy".format(vm_name)}, 201)
    return json_response({"result": return_data}, status_code)


def startThread():
    body_data = request.get_json()
    thread_provisioning = threading.Thread(target=provisioning, args=(body_data, ))
    # thread_return = threading.Thread(target=returnAccept)
    thread_provisioning.start()
    # pool = ThreadPool(processes=1)
    # async_result = pool.apply_async(provisioning, (body_data, ))
    # return_val = async_result.get()
    # if return_val == "Vapp password doesn't match":
    #     return json_response({"message": "Vapp password doesn't match"}, 400)

    return json_response({"result": "Start Provisioning"}, 202)


def statusTask():
    send_url = "http://127.0.0.1:5002/api/v1/vm/status"
    return_data = requests.request("GET", send_url)
    return_data = json.loads(return_data.text)
    print return_data
    if not return_data or return_data == [{}]:
        return json_response({"message": "Doesn't have any data"}, 200)
    else:
        return json_response({"result": return_data}, 200)
        # for each_vm in return_data:
        #     print each_vm
        #     create_status = each_vm["status"]
        #     if create_status == "Everything is success":
        #         del each_vm["status"]
        #         del each_vm["vmName"]
        #         return json_response({"result": return_data}, 200)
        #     else:
        #         return json_response({"result": return_data}, 200)


# --------------------------------------------------- Volume -----------------------------------------------------------


def checkVServer():
    # body_data = request.get_json()
    # vserver_name = "INET_TEMP_SDI"
    # return_result = vServerName()
    send_url = "http://127.0.0.1:5002/api/v1/volume/vserver"
    return_result = requests.request("GET", send_url)
    return_result = json.loads(return_result.text)
    return json_response({"result": return_result}, 200)


def checkVolume():
    # return_result = volumeName()
    send_url = "http://127.0.0.1:5002/api/v1/volume"
    return_result = requests.request("GET", send_url)
    return_result = json.loads(return_result.text)
    return json_response({"result": return_result}, 200)


def offline():
    # body_data = request.get_json()
    send_url = "http://127.0.0.1:5002/api/v1/volume/offline"
    body_data = {
        "vserverName": "INET_TEMP_SDI",
        "volumeName": "test_offline",
        "zone": "POC",
        "size": "20",
        "unitSize": "GB",
        "aggregateName": "aggr1_INET_Temp_02"
    }
    headers = {
        "platform": "flexpod"
    }
    return_result = requests.request("PUT", send_url, json=body_data, headers=headers)
    return_result = json.loads(return_result.text)
    return json_response({"message": return_result}, 200)


def returnDelete():
    # body_data = request.get_json()
    send_url = "http://127.0.0.1:5002/api/v1/volume"
    body_data = {
        "vserverName": "INET_TEMP_SDI",
        "volumeName": "test_offline",
        "zone": "POC",
        "size": "20",
        "unitSize": "GB",
        "aggregateName": "aggr1_INET_Temp_02"
    }
    headers = {
        "platform": "flexpod"
    }
    return_result = requests.request("DELETE", send_url, json=body_data, headers=headers)
    return_result = json.loads(return_result.text)
    return json_response({"message": return_result}, 200)


def getAggregate():
    # return_result = aggregateValue()
    send_url = "http://127.0.0.1:5002/api/v1/volume/aggregate"
    return_result = requests.request("GET", send_url)
    return_result = json.loads(return_result.text)
    return json_response({"result": return_result}, 200)


def returnVolume():
    body_data = request.get_json()
    send_url = "http://127.0.0.1:5002/api/v1/volume"
    # body_data = {
    #     "vserverName": "INET_TEMP_SDI",
    #     "volumeName": "test_offline",
    #     "zone": "POC",
    #     "size": "20",
    #     "unitSize": "GB",
    #     "aggregateName": "aggr1_INET_Temp_02"
    # }
    headers = {
        "platform": "flexpod"
    }
    return_result = requests.request("POST", send_url, json=body_data, headers=headers)
    return_result = json.loads(return_result.text)
    # return_result = createMainVolume(body_data)
    return json_response({"result": return_result}, 201)


# ----------------------------------------------- Network --------------------------------------------------------------


def createNSX():
    # body_data = request.get_json()
    body_data = {
        "ipInternalStart": "192.168.10.1",
        "ipInternalEnd": "192.168.10.253",
        "ipExternalStart": "203.150.67.112",
        "ipExternalEnd": "203.150.67.113",
        "vdcId": "0eeb4734-e014-4e46-a14d-b1244ced22f9",
        "customerName": "cent7_Cust"
    }
    ip_inter_start = body_data["ipInternalStart"]
    ip_intra_end = body_data["ipInternalEnd"]
    ip_extra_start = body_data["ipExternalStart"]
    ip_extra_end = body_data["ipExternalEnd"]
    # available_ip = network_config["network"]["status"]["available"]
    # unavailable_id = network_config["network"]["status"]["available"]
    # print available_ip
    network_database = getAllNetworkDB()
    for network_data_db in network_database:
        network_ip = network_data_db["network_ip"]
        network_type = network_data_db["network_type"]
        if network_ip == ip_inter_start or network_ip == ip_intra_end or network_ip == ip_extra_start or network_ip == \
                ip_extra_end:
            return json_response({"message": "IP: {}, Type: {} has already in use".format(network_ip, network_type)}, 400)
    send_url = "http://127.0.0.1:5002/api/v1/network"
    headers = {
        "platform": "flexpod"
    }
    return_result = requests.request("POST", send_url, json=body_data, headers=headers)
    return_result = return_result.text
    status_response = 201
    if status_response == 200:
        insertNetworkIp(body_data["ipInternalStart"], "IP Internal Start")
        insertNetworkIp(body_data["ipInternalEnd"], "IP Internal End")
        insertNetworkIp(body_data["ipExternalStart"], "IP External Start")
        insertNetworkIp(body_data["ipExternalEnd"], "IP External End")
    # return_result = "ok"
    print "Create NSX success"
    return json_response({"result": return_result}, 201)


def createVlan():
    body_data = request.get_json()
    send_url = "http://127.0.0.1:5002/api/v1/network/vlan"
    # body_data = {
    #     "ipInternalStart": "192.168.10.1",
    #     "ipInternalEnd": "192.168.10.253",
    #     "ipExternalStart": "203.150.67.112",
    #     "ipExternalEnd": "203.150.67.113"
    # }
    headers = {
        "platform": "flexpod"
    }
    return_result = requests.request("POST", send_url, json=body_data, headers=headers)
    return_result = json.loads(return_result.text)
    return json_response({"result": return_result})


# ------------------------------------------------- Compute ------------------------------------------------------------


def comparisonBlade():
    # body_data = request.get_json()
    send_url = "http://127.0.0.1:5002/api/v1/compute"
    # body_data = {
    #     "data": "data"
    # }
    # headers = {
    #     "platform": "flexpod"
    # }
    host_name = requests.request("GET", send_url)
    # print host_name.text
    return host_name.text


def testFlask():
    # body_data = request.get_json()
    send_url = "http://127.0.0.1:5002/api/v1/test"
    body_data = {
        "data": "data"
    }
    headers = {
        "platform": "flexpod"
    }
    host_name = requests.request("GET", send_url, json=body_data, headers=headers)
    print host_name.text
    return "ok"

