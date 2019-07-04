from flask import Flask, Response, json, request, abort, make_response, jsonify
import requests
import urllib3
from ..databases import db
import time

from ..driver.main import sendData, detailData, storageData, createMainVolume, aggregateValue, vServerName, volumeName

urllib3.disable_warnings()

sess = db.session


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


def getData():
    all_data = detailData()
    return json_response({"result": all_data}, 200)


def getStorage():
    storage_data = storageData()
    return json_response({"result": storage_data}, 200)


def provisioning():
    body_data = request.get_json()
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
    #     "name": "SampleVM",
    #     "serviceOs": "WINDOWS_8_64",
    #     "datastore": "datastore-11",
    #     "folder": "group-v3",
    #     "resourcePool": "resgroup-21",
    #     "memorySize": 4 GB,
    #     "cpuCount": 2 Core,
    #     "diskCapacity": "3 TB",
    #     "networkType": "E1000",
    #     "backingType": "STANDARD_PORTGROUP",
    #     "network": "network-13",
    #     "customerName": "L_cust_test",
    #     "orgName": "L_org_test",
    #     "vdcName": "L_vdc_test",
    #     "vAppName": "L_vapp_test",
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
        return json_response({"message": "vApp password doesn't match"}, 400)

    return_result, return_data = sendData(body_data)
    # print return_data

    if return_result is True:
        # return json_response({"message": "Your vm name {} has been deploy".format(vm_name)}, 201)
        return json_response({"result": return_data}, 201)
    else:
        return json_response({"result": return_data}, 400)


def checkVServer():
    # body_data = request.get_json()
    # vserver_name = "INET_TEMP_SDI"
    return_result = vServerName()
    return json_response({"result": return_result}, 200)


def checkVolume():
    return_result = volumeName()
    return json_response({"result": return_result}, 200)


def getAggregate():
    return_result = aggregateValue()
    return json_response({"result": return_result}, 200)


def returnStorage():
    # body_data = request.get_json()
    body_data = {
        "vserverName": "INET_TEMP_SDI",
        "volumeName": "Client",
        "zone": "POC",
        "size": "20",
        "unitSize": "GB",
        "aggregateName": "aggr1_INET_Temp_02"
    }
    return_result = createMainVolume(body_data)
    return json_response({"message": return_result}, 201)


def testFlask():
    # body_data = request.get_json()
    send_url = "http://127.0.0.1:5555/api/v1/test"
    body_data = {
        "data": "data"
    }
    headers = {
        "platform": "flexpod"
    }
    host_name = requests.request("GET", send_url, json=body_data, headers=headers)
    print host_name.text
    return "ok"

