from flask import Flask, Response, json, request, abort, make_response, jsonify
import requests
import urllib3
from ..databases import Vm, Vmspec, Template
from ..databases import db
import time
urllib3.disable_warnings()

sess = db.session


# app = Flask(__name__)


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


# get all data from database (e.g. vm, vm_spec, template)
def getAllDB(table_name):
    global sess
    resp = []
    for all_data in sess.query(table_name):  # change database here ps. don't forget import function from databases.py
        resp.append(all_data.response())
    return resp


# show database data to frontend (e.g. vm, vm_spec, template)
def getDatabaseData(table_name):
    data = getAllDB(table_name)
    print data
    return json_response({"message": data}, 200)


# insert data to database (can use this format)
def insertVm(vm_name, vm_password, vm_link, user_id, customer_id, datastore_id, vm_type):
    # change column name to insert here ---^
    global sess
    new_vm = Vm(
        # id=int(uuid.uuid4()),
        # id=id,
        vm_name=vm_name,
        vm_password=vm_password,
        vm_link=vm_link,
        user_id=user_id,
        customer_id=customer_id,
        datastore_id=datastore_id,
        type=vm_type,
        create_date=str(time.time()),
    )  # change column name to insert here
    sess.add(new_vm)
    sess.commit()


def insertTemplate(template_name, template_id, library_id, vm_id, cpu, memory, disk, os, network):

    global sess
    new_template = Template(
        # template_id_count =int(uuid.uuid4())
        template_name=template_name,
        template_id=template_id,
        library_id=library_id,
        vm_id=vm_id,
        cpu=cpu,
        memory=memory,
        disk=disk,
        os=os,
        network=network
    )
    sess.add(new_template)
    sess.commit()


def insertVmSpec(vm_id, cpu, memory, disk, os, network):

    global sess
    new_vm_spec = Template(
        # vm_id_count =int(uuid.uuid4())
        vm_id=vm_id,
        cpu=cpu,
        memory=memory,
        disk=disk,
        os=os,
        network=network
    )
    sess.add(new_vm_spec)
    sess.commit()


def returnToken():
    url = "https://10.10.21.150/rest/com/vmware/cis/session"

    headers = {
        'Authorization': "Basic YWRtaW5pc3RyYXRvckB2c3BoZXJlLmxvY2FsOjZ5SG5tanUm"
    }
    response = requests.request("POST", url, headers=headers, verify=False)
    token_value = json.loads(response.text)
    basic_token = token_value["value"]
    return basic_token


# @app.route("/vmname/<string:vm_name>", methods=['GET'])
# def vmName(vm_name):
#     token_number = returnToken()
#
#     url = "https://10.10.21.150/rest/vcenter/vm"
#
#     headers = {
#         'vmware-api-session-id': "{}".format(token_number)
#     }
#     response = requests.request("GET", url, headers=headers, verify=False)
#     raw_data = json.loads(response.text)
#     raw_value = raw_data["value"]
#     for name_checking in raw_value:
#         api_name = str(name_checking["name"])
#         # print api_name
#         if vm_name == api_name:
#             return json_response({"message": "This vm name has already in use"}, 400)
#         else:
#             pass
#     return json_response({"message": "Can use this vm name"}, 200)


def vmName():
    token_number = returnToken()

    url = "https://10.10.21.150/rest/vcenter/vm"

    headers = {
        'vmware-api-session-id': "{}".format(token_number)
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    raw_data = json.loads(response.text)
    raw_value = raw_data["value"]
    # for name_checking in raw_value:
    #     api_name = str(name_checking["name"])
    #     # print api_name
    #     if vm_name == api_name:
    #         return "This vm name has already in use"
    #     else:
    #         pass
    return raw_value


# @app.route("/storage", methods=['GET'])
def getStorage():
    token_number = returnToken()
    url = "https://10.10.21.150/rest/vcenter/datastore"

    headers = {
        'vmware-api-session-id': "{}".format(token_number)
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    # print response.status_code
    # if response.status_code == 200:
    #     print "yes"
    # else:
    #     print "no"
    raw_data = json.loads(response.text)
    raw_value = raw_data["value"]
    result_list = []
    for store_data in raw_value:
        datastore = store_data["datastore"]
        name = store_data["name"]
        capacity_value = store_data["capacity"]
        free_value = store_data["free_space"]
        free_percentage = round(float((free_value*100)/capacity_value), 1)

        result_dict = {
            "datastore": datastore,
            "name": name,
            "freePercentage": float(free_percentage)
        }
        # print result_dict["free_space"]
        result_list.append(result_dict)
    return result_list
    # return json_response({"message": result_list}, 200)


# @app.route("/templates", methods=['GET'])
def getTemplates():
    token_number = returnToken()
    url = "https://10.10.21.150/rest/com/vmware/content/local-library"

    headers = {
        'vmware-api-session-id': "{}".format(token_number)
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    raw_data = json.loads(response.text)
    template_list = raw_data["value"]
    result_list = []
    for template_id in template_list:
        url = "https://10.10.21.150/rest/com/vmware/content/local-library/id:{}".format(
            template_id
        )

        headers = {
            'vmware-api-session-id': "{}".format(token_number)
        }

        response = requests.request("GET", url, headers=headers, verify=False)
        template_data = json.loads(response.text)

        url = "https://10.10.21.150/rest/com/vmware/content/library/item"

        querystring = {"library_id": "{}".format(template_id)}

        headers = {
            'vmware-api-session-id': "{}".format(token_number)
        }

        response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
        library_data = json.loads(response.text)
        if library_data["value"] == []:
            result_dict = {
                "template_id": template_id,
                "template_name": template_data["value"]["name"],
                "library_item": None
            }
            result_list.append(result_dict)
        else:
            library_id_list = library_data["value"]
            sub_result_list = []
            for library_id in library_id_list:
                url = "https://10.10.21.150/rest/com/vmware/content/library/item/id:{}".format(library_id)

                headers = {
                    'vmware-api-session-id': "{}".format(token_number)
                }

                response = requests.request("GET", url, headers=headers, verify=False)
                sub_library_data = json.loads(response.text)
                sub_result_dict = {
                    "library_id": library_id,
                    "library_name": sub_library_data["value"]["name"]
                }
                sub_result_list.append(sub_result_dict)
            result_dict = {
                "template_id": template_id,
                "template_name": template_data["value"]["name"],
                "library_item": sub_result_list
            }
            result_list.append(result_dict)
    return json_response({"message": result_list}, 200)


# @app.route("/template/<string:template_id>", methods=['GET'])
def getTemplateId(template_id):
    try:
        token_number = returnToken()
        result_list = []
        url = "https://10.10.21.150/rest/com/vmware/content/local-library/id:{}".format(
            template_id
        )

        headers = {
            'vmware-api-session-id': "{}".format(token_number)
        }
        response = requests.request("GET", url, headers=headers, verify=False)
        template_data = json.loads(response.text)

        url = "https://10.10.21.150/rest/com/vmware/content/library/item"

        querystring = {"library_id": "{}".format(template_id)}

        headers = {
            'vmware-api-session-id': "{}".format(token_number)
        }
        response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
        library_data = json.loads(response.text)
        if library_data["value"] == []:
            result_dict = {
                "template_id": template_id,
                "template_name": template_data["value"]["name"],
                "library_item": None
            }
            result_list.append(result_dict)
        else:
            library_id_list = library_data["value"]
            sub_result_list = []
            for library_id in library_id_list:
                url = "https://10.10.21.150/rest/com/vmware/content/library/item/id:{}".format(library_id)

                headers = {
                    'vmware-api-session-id': "{}".format(token_number)
                }
                response = requests.request("GET", url, headers=headers, verify=False)
                sub_library_data = json.loads(response.text)
                sub_result_dict = {
                    "library_id": library_id,
                    "library_name": sub_library_data["value"]["name"]
                }
                sub_result_list.append(sub_result_dict)
            result_dict = {
                "template_id": template_id,
                "template_name": template_data["value"]["name"],
                "library_item": sub_result_list
            }
            result_list.append(result_dict)
        return json_response({"message": result_list}, 200)
    except Exception:
        return json_response({"message": "mistake template id"}, 400)


# @app.route("/networks", methods=['GET'])
def getNetworks():
    token_number = returnToken()
    url = "https://10.10.21.150/rest/vcenter/network"

    headers = {
        'vmware-api-session-id': "{}".format(token_number)
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    raw_data = json.loads(response.text)
    raw_value = raw_data["value"]
    return json_response({"message": raw_value}, 200)


# # @app.route("/deploy", methods=['POST'])
# def deployMachine():
#     try:
#         data = {
#             # data that i want
#             "name": "VM_3",
#             "storage": "datastore-12",
#             "storage_type": "thin",
#             "template_id": "e05ab043-9f0f-47bb-85dc-d829df388c08",
#             "template_name": "Template_Windows2012_prd_api",
#             "network_id": "Don't know",
#             "network_name": "VXLAN-DVUplinks-25 or dvportgroup-26",
#             "username": "mai dai tum wai"
#         }
#         body_data = request.get_json()
#         # body_data = data
#         checking_key, missing_key = checkParameter(body_data.keys(), ["name", "storage", "storage_type", "template_id",
#                     "template_name", "network_id", "network_name"])
#         if checking_key:
#             pass
#         else:
#             return json_response({"message": "Missing parameters: " + ",".join(missing_key)}, 400)
#         template_id = body_data["template_id"]
#         vm_name = body_data["name"]
#         data_storage = body_data["storage"]
#         storage_type = body_data["storage_type"]
#
#         token_number = returnToken()
#
#         url = "https://10.10.21.150/rest/com/vmware/vcenter/ovf/library-item/id:{}".format(
#             template_id
#         )
#
#         querystring = {"~action": "deploy"}
#
#         payload_data = {
#             "deployment_spec":
#             {
#                "accept_all_EULA": True,
#                "name": vm_name,
#                "default_datastore_id": data_storage,
#
#                "storage_provisioning": storage_type,
#                "additional_parameters": [
#                    {
#                        "@class": "com.vmware.vcenter.ovf.property_params",
#                        "properties": [
#                            {
#                                "instance_id": "",
#                                "class_id": "",
#                                "description": "The gateway IP for this virtual appliance.",
#                                "id": "gateway",
#                                "label": "Default Gateway Address",
#                                "category": "LAN",
#                                "type": "ip",
#                                "value": "10.1.2.1",
#                                "ui_optional": True
#                            }
#                        ],
#                        "type": "PropertyParams"
#                    }
#                ]
#            },
#             "target": {
#                 "folder_id": "group-v3",
#                 "host_id": "host-9",
#                 "resource_pool_id": "resgroup-21"
#             }
#         }
#
#         headers = {
#             'Content-Type': "application/json",
#             'vmware-api-session-id': "{}".format(token_number)
#         }
#         payload_data = json.dumps(payload_data)
#         # response = requests.request("POST", url, data=payload_data, headers=headers, params=querystring, verify=False)
#         # print(response.text)
#         response = 200
#
#         vm_password = "123456"
#         vm_link = "link"
#         user_id = 1
#         customer_id = 1
#         vm_type = "temp"
#
#         vm_table = getAllDB(Vm)
#         for i in vm_table:
#             print i["vm_id"]
#
#         if response == 200 or response == 201 or response == 202:
#             pass
#         # if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
#         #     insertVm(vm_name, vm_password, vm_link, user_id, customer_id, data_storage, vm_type)
#         else:
#             json_response({"message": "Error deploy your vm"}, 400)
#
#         return json_response({"message": "Your vm name {} has been deploy".format(vm_name)}, 201)
#     except Exception as e:
#         return json_response({"message": "Error deploy your vm"}, 400)
#
#
# # @app.route("/deploy/config", methods=['POST'])
# def deploySpecialMachine():
#     url = "https://10.10.21.150/rest/vcenter/vm"
#
#     token_number = returnToken()
#
#     data = {
#         # data that i want
#         "name": "SampleVM",
#         "service_os": "WINDOWS_8_64",
#         "datastore": "datastore-11",
#         "folder": "group-v3",
#         "resource_pool": "resgroup-21",
#         "memory_size": 4,
#         "cpu_count": 2,
#         "disk_capacity": "3TB",
#         "network_type": "E1000",
#         "backing_type": "STANDARD_PORTGROUP",
#         "network": "network-13"
#     }
#     # body_data = request.get_json()
#     body_data = data
#     checking_key, missing_key = checkParameter(body_data.keys(), ["name", "service_os", "datastore", "folder",
#         "resource_pool", "memory_size", "cpu_count", "disk_capacity", "network_type", "backing_type", "network"])
#     if checking_key:
#         pass
#     else:
#         return json_response({"message": "Missing parameters: " + ",".join(missing_key)}, 400)
#     vm_name = body_data["name"]
#     service_os = body_data["service_os"]
#     datastore = body_data["datastore"]
#     folder = body_data["folder"]
#     resource_pool = body_data["resource_pool"]
#     memory_size = body_data["memory_size"]
#     cpu_count = body_data["cpu_count"]
#
#     disk_capacity = body_data["disk_capacity"]
#     disk_value = int(disk_capacity[0])
#     disk_unit = disk_capacity[1:3]
#
#     if disk_unit == "TB":
#         disk_real_value = disk_value * (1024 ** 4)
#     else:
#         disk_real_value = disk_value * (1024 ** 3)
#
#     network_type = body_data["network_type"]
#     backing_type = body_data["backing_type"]
#     network = body_data["network"]
#
#     payload_data = {
#             "spec": {
#                 "name": vm_name,
#                 "guest_OS": service_os,
#                 "placement" : {
#                     "datastore": datastore,
#                     "folder": folder,
#                     "resource_pool": resource_pool
#                 },
#                 "memory": {
#                   "size_MiB": memory_size,
#                   "hot_add_enabled": True
#                 },
#                 "floppies": [],
#                 "cpu": {
#                   "hot_remove_enabled": True,
#                   "count": cpu_count,
#                   "hot_add_enabled": True,
#                   "cores_per_socket": 1
#                 },
#                 "cdroms": [
#                     {
#                         "type": "IDE",
#                         "backing": {
#                             "iso_file": "[datastore1] photon-minimal-1.0TP2.iso",
#                             "type": "ISO_FILE"
#                         }
#                     }
#                 ],
#                 "disks": [
#                     {
#                         "new_vmdk": {
#                             "capacity": disk_real_value
#                         }
#                     }
#                 ]
#             }
#         }
#     headers = {
#         'Content-Type': "application/json",
#         'vmware-api-session-id': "{}".format(token_number)
#     }
#
#     payload = json.dumps(payload_data)
#     # response = requests.request("POST", url, data=payload, headers=headers, verify=False)
#
#     # deploy_vm = response.text
#     # deploy_vm = json.loads(deploy_vm)
#     deploy_vm = {"value": "vm-108"}
#     vm_id = deploy_vm["value"]
#
#     url = "https://10.10.21.150/rest/vcenter/vm/{}/hardware/ethernet".format(vm_id)
#
#     payload_data = {
#         "spec": {
#             "type": network_type,
#             "backing": {
#                 "type": backing_type,
#                 "network": network
#             }
#         }
#     }
#     headers = {
#         'Content-Type': "application/json",
#         'vmware-api-session-id': "{}".format(token_number)
#     }
#
#     payload = json.dumps(payload_data)
#     # requests.request("POST", url, data=payload, headers=headers, verify=False)
#
#     return json_response({"message": "Your vm name {} has been deploy".format(vm_name)}, 201)


# @app.route("/deploy", methods=['POST'])
def deployMachine(data):
    error_data = {"CreateError": "Can't deploy vm from template"}
    try:
        # data = {
        #     # data that i want
        #     "name": "VM_3",
        #     "storage": "datastore-12",
        #     "storage_type": "thin",
        #     "template_id": "e05ab043-9f0f-47bb-85dc-d829df388c08",
        #     "template_name": "Template_Windows2012_prd_api",
        #     "network_id": "Don't know",
        #     "network_name": "VXLAN-DVUplinks-25 or dvportgroup-26",
        #     "username": "mai dai tum wai"
        # }
        # body_data = request.get_json()
        body_data = data
        checking_key, missing_key = checkParameter(body_data.keys(), ["name", "storage", "storageType",
                    "templateName", "networkId", "networkName"])
        if checking_key:
            pass
        else:
            # return json_response({"message": "Missing parameters: " + ",".join(missing_key)}, 400)
            return False, {"message": "Missing parameters: " + ",".join(missing_key)}
        template_id = body_data["templateId"]
        vm_name = body_data["name"]
        data_storage = body_data["storage"]
        storage_type = body_data["storageType"]

        token_number = returnToken()

        url = "https://10.10.21.150/rest/com/vmware/vcenter/ovf/library-item/id:{}".format(
            template_id
        )

        querystring = {"~action": "deploy"}

        payload_data = {
            "deployment_spec":
            {
               "accept_all_EULA": True,
               "name": vm_name,
               "default_datastore_id": data_storage,

               "storage_provisioning": storage_type,
               "additional_parameters": [
                   {
                       "@class": "com.vmware.vcenter.ovf.property_params",
                       "properties": [
                           {
                               "instance_id": "",
                               "class_id": "",
                               "description": "The gateway IP for this virtual appliance.",
                               "id": "gateway",
                               "label": "Default Gateway Address",
                               "category": "LAN",
                               "type": "ip",
                               "value": "10.1.2.1",
                               "ui_optional": True
                           }
                       ],
                       "type": "PropertyParams"
                   }
               ]
           },
            "target": {
                "folder_id": "group-v3",
                "host_id": "host-9",
                "resource_pool_id": "resgroup-21"
            }
        }

        headers = {
            'Content-Type': "application/json",
            'vmware-api-session-id': "{}".format(token_number)
        }
        payload_data = json.dumps(payload_data)
        response = requests.request("POST", url, data=payload_data, headers=headers, params=querystring, verify=False)
        deploy_vm = response.text
        deploy_vm = json.loads(deploy_vm)
        vm_id = deploy_vm["value"]["resource_id"]["id"]
        body_data["vmId"] = vm_id
        # print vm_id
        # response = 200
        #
        # vm_password = "123456"
        # vm_link = "link"
        # user_id = 1
        # customer_id = 1
        # vm_type = "temp"
        #
        # vm_table = getAllDB(Vm)
        # for i in vm_table:
        #     print i["vm_id"]
        #
        # if response == 200 or response == 201 or response == 202:
        #     pass
        # # if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
        # #     insertVm(vm_name, vm_password, vm_link, user_id, customer_id, data_storage, vm_type)
        # else:
        #     json_response({"message": "Error deploy your vm"}, 400)
        if response.status_code == 200:
        # if response == 200:
            return True, body_data
        else:
            return False, error_data
    except Exception as e:
        return False, error_data


# @app.route("/deploy/config", methods=['POST'])
def deploySpecialMachine(data):
    error_data = {"CreateError": "Can't deploy vm"}
    try:
        url = "https://10.10.21.150/rest/vcenter/vm"

        token_number = returnToken()

        # data = {
        #     # data that i want
        #     "name": "SampleVM",
        #     "service_os": "WINDOWS_8_64",
        #     "datastore": "datastore-11",
        #     "folder": "group-v3",
        #     "resource_pool": "resgroup-21",
        #     "memory_size": 4,
        #     "cpu_count": 2,
        #     "disk_capacity": "3TB",
        #     "network_type": "E1000",
        #     "backing_type": "STANDARD_PORTGROUP",
        #     "network": "network-13"
        # }
        # body_data = request.get_json()
        body_data = data
        checking_key, missing_key = checkParameter(body_data.keys(), ["name", "serviceOs", "datastore", "folder",
            "resourcePool", "memorySize", "cpuCount", "diskCapacity", "networkType", "backingType", "network"])
        if checking_key:
            pass
        else:
            # return json_response({"message": "Missing parameters: " + ",".join(missing_key)}, 400)
            return False, {"message": "Missing parameters: " + ",".join(missing_key)}
        vm_name = body_data["name"]
        service_os = body_data["serviceOs"]
        datastore = body_data["datastore"]
        folder = body_data["folder"]
        resource_pool = body_data["resourcePool"]
        memory_size = int(body_data["memorySize"].split()[0])
        cpu_count = int(body_data["cpuCount"].split()[0])

        disk_capacity = body_data["diskCapacity"].split()
        disk_value = int(disk_capacity[0])
        disk_unit = disk_capacity[1]

        if disk_unit == "TB":
            disk_real_value = disk_value * (1024 ** 4)
        else:
            disk_real_value = disk_value * (1024 ** 3)

        network_type = body_data["networkType"]
        backing_type = body_data["backingType"]
        network = body_data["network"]

        payload_data = {
                "spec": {
                    "name": vm_name,
                    "guest_OS": service_os,
                    "placement" : {
                        "datastore": datastore,
                        "folder": folder,
                        "resource_pool": resource_pool
                    },
                    "memory": {
                      "size_MiB": memory_size,
                      "hot_add_enabled": True
                    },
                    "floppies": [],
                    "cpu": {
                      "hot_remove_enabled": True,
                      "count": cpu_count,
                      "hot_add_enabled": True,
                      "cores_per_socket": 1
                    },
                    "cdroms": [
                        {
                            "type": "IDE",
                            "backing": {
                                "iso_file": "[datastore1] photon-minimal-1.0TP2.iso",
                                "type": "ISO_FILE"
                            }
                        }
                    ],
                    "disks": [
                        {
                            "new_vmdk": {
                                "capacity": disk_real_value
                            }
                        }
                    ]
                }
            }
        headers = {
            'Content-Type': "application/json",
            'vmware-api-session-id': "{}".format(token_number)
        }

        payload = json.dumps(payload_data)
        response = requests.request("POST", url, data=payload, headers=headers, verify=False)

        # response = 200
        # print response.status_code
        if response.status_code != 200:
        # if response != 200:
            return False, error_data
        else:
            pass

        deploy_vm = response.text
        deploy_vm = json.loads(deploy_vm)
        # deploy_vm = {"value": "vm-108"}
        vm_id = deploy_vm["value"]
        body_data["vmId"] = vm_id

        url = "https://10.10.21.150/rest/vcenter/vm/{}/hardware/ethernet".format(vm_id)

        payload_data = {
            "spec": {
                "type": network_type,
                "backing": {
                    "type": backing_type,
                    "network": network
                }
            }
        }
        headers = {
            'Content-Type': "application/json",
            'vmware-api-session-id': "{}".format(token_number)
        }

        payload = json.dumps(payload_data)
        response = requests.request("POST", url, data=payload, headers=headers, verify=False)
        # print response.status_code
        # response = 200
        if response.status_code == 200:
        # if response == 201:
            return True, body_data
        else:
            return False, error_data
    except Exception as e:
        return False, error_data


# if __name__ == '__main__':
#     app.run(debug=True, port=8080, host='127.0.0.1')

