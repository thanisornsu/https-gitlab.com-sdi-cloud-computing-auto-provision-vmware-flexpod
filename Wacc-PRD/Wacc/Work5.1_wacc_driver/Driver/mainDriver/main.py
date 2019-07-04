from flask import Flask, jsonify, request
import requests
from ..flexpod.vCenter import *
from ..flexpod.vCloud import *
from ..flexpod.volume import *
from ..flexpod.nsx import *
from ..flexpod.compute import *
from yaml import load


provisioning_dict = {}
provisioning_list = []


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


def testdata():
    test = request.json
    header = request.headers
    print test
    print header
    return "Yes"


def checkAuthen(username, password):
    # get_data = request.json
    get_data = {"username": "obesity01",
                "password": "12345d"}
    # print get_data
    # username_Test = "obesity01"
    # password_test = "12345d"

    # print get_data["username"]
    # print get_data["password"]

    if get_data["username"] != username:
        return "invalid username", 400
    if get_data["password"] != password:
        return "invalid password", 400
    # data_gen = get_data["username"] + "#" + get_data["password"]
    # encoded_data = base64.b64encode(data_gen)
    # autho = str(encoded_data)
    # token_head = {
    #     'Authorization': autho,
    #     "status": "success"
    # }
    # global autho
    # print "v"
    return True


# ---------------------------------------------- Provisioning ----------------------------------------------------------


def detailData():
    vm_data = vmName()
    if vm_data == "This vm name has already in use":
        return json.dumps("This vm name has already in use")
    else:
        # return json_response({"result": vm_data}, 200)
        return json.dumps(vm_data)


def storageData():
    storage_data = getStorage()
    print storage_data
    return json.dumps(storage_data)


def orgData():
    org_list, condition = queryOrg()
    # print org_list
    return json.dumps(org_list)


def vdcData(org_name):
    vdc_data = queryVdc(org_name)
    return json.dumps(vdc_data)


def vappData(org_name, vdc_name):
    vapp_data = queryVapp(org_name, vdc_name)
    return json.dumps(vapp_data)


# def createOther(condition_case, data, frontend_data):
#     dict_result = {}
#     if condition_case is True:
#         condition, return_data = mainVcloud(data)
#         if condition is True:
#             # print condition
#             print return_data
#             dict_result["orgName"] = return_data["org_name"]
#             dict_result["orgUrl"] = return_data["org_url"]
#             dict_result["orgId"] = return_data["org_id"]
#             dict_result["vmName"] = return_data["vm_name"]
#             dict_result["vmId"] = return_data["vm_id"]
#             dict_result["vdcName"] = return_data["vdc_name"]
#             dict_result["vdcId"] = return_data["vdc_id"]
#             dict_result["vApp_username"] = return_data["user_name"]
#             dict_result["vApp_password"] = return_data["vapp_user_password"]
#             # return True, dict_result
#             condition, return_data = all_network(dict_result, frontend_data)
#             if condition is True:
#                 print return_data
#                 return True, dict_result
#             else:
#                 return False, return_data
#         else:
#             return False, return_data
#     else:
#         return False, dict_result
#     return "vCenter ready", dict_result


def mainVcloud(data):
    global provisioning_dict
    customer_name = data["customerName"]
    zone = data["zone"]
    cpu = data["cpuCount"].split()[0]
    mem = data["memorySize"].split()[0]
    disk = data["diskCapacity"].split()[0]

    vm_name = data["name"]
    vm_id = data["vmId"]
    # vdc_id = "e5c3bc5f-e070-4398-bebd-a03ecd14c176"
    vapp_username = data["vAppUser"]
    vapp_user_password = data["vAppPassword"]
    cluster = getVcenterVcloudDetail("test")
    vcloud_token = create_sessions(cluster["vcloud_ip"],cluster["vcloud_username"],cluster["vcloud_password"])
    org,err = create_org_on_vcloud(cluster,vcloud_token,customer_name)
    if not err:
        # print "test_vdc"
        provisioning_dict["status"] = "Create org on vcloud success"
        vdc, vdc_err = create_vdc_on_vcloud(cluster, vcloud_token, org['org_id'], customer_name, zone, cpu, mem, disk)
        # print vdc["vdc_id"]
        # print vdc_err
        if not vdc_err:
            # print "do more"
            provisioning_dict["status"] = "Create vdc on vcloud success"
            vapp, vapp_err = add_vm_to_cloud(cluster, vcloud_token, vm_name, vdc["vdc_id"], customer_name, vm_id)
            # print vapp_err
            if not vapp_err:
                # print "do it"
                provisioning_dict["status"] = "Add vm to vcloud success"
                # result_dict = {}
                result_dict = org.copy()
                result_dict.update(vdc)
                result_dict.update(vapp)
                user, user_err = createvAppUser(vapp_username, vapp_user_password, cluster["vcloud_ip"], vcloud_token,
                                                org['org_id'])
                if not user_err:
                    # print "Create user vapp"
                    provisioning_dict["status"] = "Create vapp user success"
                    result_dict.update(user)
                    # print result_dict, "Last MainVcloud"
                    return True, result_dict
                else:
                    provisioning_dict["status"] = "Can't create vapp user"
                    return False, {"CreateError": "Can't create vapp user"}
            else:
                print "can not create vApp"
                provisioning_dict["status"] = "Can't add vm to vcloud"
                return False, {"CreateError": "Can't create vApp"}
        else:
            print "cannot create vdc"
            provisioning_dict["status"] = "Can't create vdc"
            return False, {"CreateError": "Can't create vdc"}
        # return False, {"Create Organize": "Can't create organize"}
    else:
        print "error create organize"
        provisioning_dict["status"] = "Error create organize"
        return False, {"CreateError": "Can't create organize"}


def sendData():
    global provisioning_dict
    front_data = request.json
    config_data = front_data
    provisioning_dict = {
        "vmName": config_data["name"],
        "status": "Provisioning VM"
                         }
    provisioning_list.append(provisioning_dict)
    print provisioning_dict
    if front_data.has_key("templateName"):
        get_template = front_data["templateName"]
        with open('Driver\\flexpod\config.yaml') as f:
        # with open('/home/sdiadmin/Web-app/wacc-app/WebAppControlCenter/driver/config.yaml') as f:
            yaml_data = load(f)
            template_name = yaml_data["template"]
            for each_template in template_name:
                if each_template["template_name"] == get_template:
                    template_id = each_template["template_id"]
                    # template_cpu = each_template["CPU"]
                    # template_mem = each_template["Memory"]
                    # template_disk = each_template["Disk"]
                    front_data["templateId"] = template_id
                    # front_data["cpuCount"] = template_cpu
                    # front_data["memorySize"] = template_mem
                    # front_data["diskCapacity"] = template_disk
                    # deployMachine(receive_data)
                    condition, return_data = deployMachine(front_data)
                    if front_data["provisionStatus"] is True:
                        vm_id = return_data["vmId"]
                        cpu_spec = config_data["cpuCount"].split(" ")[0]
                        mem_spec = config_data["memorySize"].split(" ")[0]
                        disk_spec = config_data["diskCapacity"].split(" ")[0]
                        upgradeCpu(vm_id, cpu_spec)
                        upgradeMemory(vm_id, mem_spec)
                    if condition is True:
                        print condition, "Template True"
                        provisioning_dict["status"] = "Create VM success"
                        return_case, dict_result = mainVcloud(return_data)
                        # return_case, dict_result = createOther(condition, return_data, front_data)
                        dict_result["vmName"] = return_data["name"]
                        dict_result["vmId"] = return_data["vmId"]
                        dict_result["storage"] = return_data["storage"]
                        dict_result["storageType"] = return_data["storageType"]
                        dict_result["networkName"] = return_data["networkName"]
                        dict_result["templateName"] = each_template["template_name"]
                        if front_data["provisionStatus"] is True:
                            dict_result["cpu"] = config_data["cpuCount"]
                            dict_result["memory"] = config_data["memorySize"]
                            dict_result["disk"] = config_data["diskCapacity"]
                            provisioning_dict["status"] = "Everything is success"
                        else:
                            dict_result["cpu"] = each_template["CPU"]
                            dict_result["memory"] = each_template["Memory"]
                            dict_result["disk"] = each_template["Disk"]
                            provisioning_dict["status"] = "Everything is success"
                        dict_result["statusCode"] = 201
                        return json.dumps(dict_result)
                    else:
                        print condition, "Template False"
                        provisioning_dict["status"] = "Doesn't Vm to deploy (template)"
                        return_data["statusCode"] = 400
                        return json.dumps(return_data)
                else:
                    pass
    else:
        # deploySpecialMachine(receive_data)
        condition, return_data = deploySpecialMachine(front_data)
        # print return_data
        if condition is True:
            print condition, "Config True"
            # print return_data
            return_case, dict_result = mainVcloud(return_data)
            # return_case, dict_result = createOther(condition, return_data, front_data)
            dict_result["vmName"] = return_data["name"]
            dict_result["vmId"] = return_data["vmId"]
            dict_result["serviceOs"] = return_data["serviceOs"]
            dict_result["cpuCount"] = return_data["cpuCount"]
            dict_result["memorySize"] = return_data["memorySize"]
            dict_result["diskCapacity"] = return_data["diskCapacity"]
            dict_result["datastore"] = return_data["datastore"]
            dict_result["network"] = return_data["network"]
            dict_result["networkType"] = return_data["networkType"]
            dict_result["statusCode"] = 201
            return json.dumps(dict_result)
        else:
            print condition, "Config False"
            return_data["Result"] = "Doesn't Vm to deploy"
            return_data["statusCode"] = 400
            return json.dumps(return_data)


def statusTask():
    global provisioning_dict
    global provisioning_list
    print provisioning_list
    old_vm_list = []
    old_status = ""
    try:
        if not provisioning_list:
            pass
        else:
            new_vm_name = provisioning_dict["vmName"]
            print new_vm_name
            for vm_return in provisioning_list:
                old_vm_name = vm_return["vmName"]
                old_status = vm_return["status"]
                old_vm_list.append(old_vm_name)
            if new_vm_name not in old_vm_list:
                provisioning_list.append(provisioning_dict)
            if old_status == "Everything is success":
                old_vm_list.remove(provisioning_dict["vmName"])
                provisioning_list.remove(provisioning_dict)
                provisioning_dict.clear()
        return_data = provisioning_list
        return json.dumps(return_data)
    except Exception as e:
        empty_list = []
        return json.dumps(empty_list)


# ----------------------------------------------- Volume ---------------------------------------------------------------


def vServerName():
    v_name = "INET_TEMP_SDI"
    # vserver_name, condition = checkVserver(v_name)
    vserver_name, condition = checkVserver()
    return json.dumps(vserver_name)


def volumeName():
    volume_name, condition = checkVolume()
    return json.dumps(volume_name)


def checkStatus():
    get_data = request.json
    # vserver_name = get_data["vserverName"]
    # volume_name = get_data["volumeName"]
    status, condition = offlineStatus(get_data)
    return json.dumps(status)


def aggregateValue():
    aggregate = getAggregate()
    return json.dumps(aggregate)


def volumeDelete():
    get_data = request.json
    # vserver_name = get_data["vserverName"]
    # volume_name = get_data["volumeName"]
    delete = deleteVolume(get_data)
    return json.dumps(delete)


def createMainVolume():
    all_data = request.json
    build = mainBuildStorage(all_data)
    return json.dumps(build)
    # return json.dumps("ok")


# ------------------------------------------------ Network -------------------------------------------------------------


def edge():
    try:
        # header = request.headers
        header = {"BD": "flexpod"}
        # data = request.json
        data = {"customer_name" : "Obesity01",
                "vdc_id" : "82f1f86a-a56a-4bc6-a73f-4bda0b2792e7",
                "ip_external_start" : "203.150.67.112",
                "ip_external_end" : "203.150.67.113"  }
        # print data["customer_name"], "name"
        # print data["vdc_id"], "vdc id"
        # print data["ip_external_start"], "ip externaml start"
        # print data["ip_external_end"], "ip external end"
        cluster = getVcenterVcloudDetail("test")
        vcloud_token = create_sessions(cluster)
        # print vcloud_token, "debug"
        external_network,err = external_network_id(vcloud_token)
        if not err:
            print "pass"
            # print external_network,"test"
            edge, err = create_edge(vcloud_token, data["vdc_id"], data["ip_external_start"], data["ip_external_end"], external_network, data["customer_name"])
            if not err:
                print "success"
                dict = {"header" : header,
                        "customer_name": data["customer_name"],
                        "ip_external_start": data["ip_external_start"],
                        "ip_external_end": data["ip_external_end"],
                        "message": "You create edge network success already."}

                return json.dumps(dict)
            else:
                dict = {"message" : "You can not create edge network."}
                return json.dumps(dict)
        else:
            dict = {"message": "You can not create edge network success already."}
            return json.dumps(dict)

    except Exception as e:
        print "stop\n"
        dict = {"message": "You can not create edge network success already."}
        return json.dumps(dict)


def vdc_network():
    try:
        # header = request.headers
        header = {"BD": "flexpod"}
        # data = request.json
        data = {"customer_name" : "Obesity",
                "vdc_id" : "82f1f86a-a56a-4bc6-a73f-4bda0b2792e7",
                "ip_internal_start" : "192.168.10.1",
                "ip_internal_end" : "192.168.10.253"  }
        print data["customer_name"], "name"
        print data["vdc_id"], "vdc id"
        print data["ip_internal_start"], "ip internal start"
        print data["ip_internal_end"], "ip_internal_end"
        cluster = getVcenterVcloudDetail("test")
        # print cluster["vcloud_ip"]
        # print cluster["vcloud_username"]
        # print cluster["vcloud_password"]
        ip_gateway = "192.168.0.254"
        print "as"
        vcloud_token = create_sessions(cluster)
        print vcloud_token, "debug"
        gateway_id, err = edgeGateways(vcloud_token, data["vdc_id"])
        if not err:
            vdc_network,err = org_vdc_network(vcloud_token, data["vdc_id"], data["ip_internal_start"], data["ip_internal_end"], gateway_id, data["customer_name"])
            if not err:
                print "create org_vdc_network success"
                dict = {"header": header,
                        "customer_name": data["customer_name"],
                        "ip_internal_start": data["ip_internal_start"],
                        "ip_internal_end": data["ip_internal_end"],
                        "message": "You create org_vdc_network success already."}
                return json.dumps(dict)
            else:
                dict = {"message": "You can not create org_vdc_network."}
                return json.dumps(dict)
        else:
            dict = {"message": "You can not create org_vdc_network."}
            return json.dumps(dict)

    except Exception as e:
        print e
        dict = {"message": "You can not create org_vdc_network."}
        return json.dumps(dict)


def nat():
    try:
        # header = request.headers
        header = {"BD": "flexpod"}
        # data = request.json
        data = {"customer_name" : "Obesity",
                "vdc_id" : "82f1f86a-a56a-4bc6-a73f-4bda0b2792e7",
                "ip_internal_start" : "192.168.10.1",
                "ip_external_end" : "203.150.67.113"  }
        print data["customer_name"], "name"
        print data["vdc_id"], "vdc id"
        print data["ip_internal_start"], "ip internal start"
        print data["ip_external_end"], "ip_external_end"
        cluster = getVcenterVcloudDetail("test")
        ip_gateway = "192.168.0.254"
        vcloud_token = create_sessions(cluster)
        gateway_id, err = edgeGateways(vcloud_token, data["vdc_id"])
        if not err:
            id_network, err = org_vdc_network_id(vcloud_token)
            if not err:
                modify_nat(vcloud_token, gateway_id, data["ip_external_end"], data["ip_internal_start"], id_network)
                print "create org_vdc_network success"
                dict = {"header": header,
                        "customer_name": data["customer_name"],
                        "ip_internal_start": data["ip_internal_start"],
                        "ip_external_end": data["ip_external_end"],
                        "message": "You connect Nat success already."}
                return json.dumps(dict)
            else:
                dict = {"message": "You can not connect Nat."}
                return json.dumps(dict)
        else:
            dict = {"message": "You can not connect Nat."}
            return json.dumps(dict)

    except Exception as e:
        print e
        dict = {"message": "You can not connect Nat."}
        return json.dumps(dict)


def network_vapp():
    try:
        # header = request.headers
        header = {"BD": "flexpod"}
        # data = request.json
        data = {"customer_name" : "Obesity",
                "vdc_id" : "82f1f86a-a56a-4bc6-a73f-4bda0b2792e7",
                "ip_internal_start" : "192.168.10.1",
                "ip_internal_end" : "192.168.10.253"  }
        print data["customer_name"], "name"
        print data["vdc_id"], "vdc id"
        print data["ip_internal_start"], "ip internal start"
        print data["ip_internal_end"], "ip_internal_end"
        ip_gateway = "192.168.0.254"
        netmask = "255.255.255.0"
        cluster = getVcenterVcloudDetail("test")
        vcloud_token = create_sessions(cluster)
        id_network, err = org_vdc_network_id(vcloud_token)
        if not err:
            vapp, err = vapp_id(vcloud_token, data["vdc_id"])
            network_vapp,err = add_network_vapp(vcloud_token,vapp, data["customer_name"], ip_gateway, netmask,data["ip_internal_start"], data["ip_internal_end"], id_network)
            if not err:
                print "create org_vdc_network success"
                dict = {"header": header,
                        "customer_name": data["customer_name"],
                        "ip_internal_start": data["ip_internal_start"],
                        "ip_internal_end" : data["ip_internal_end"],
                        "message": "You connect network vapp success already."}
                return json.dumps(dict)
            else:
                print "what"
                dict = {"message": "You can not connect network vapp."}
                return json.dumps(dict)
        else:
            dict = {"message": "You can not connect network vapp."}
            return json.dumps(dict)


    except Exception as e:
        print e
        dict = {"message": "You can not connect network vapp."}
        return json.dumps(dict)


def vm_network():
    try:
        # header = request.headers
        header = {"BD": "flexpod"}
        # data = request.json
        data = {"customer_name": "Obesity",
                "vdc_id": "82f1f86a-a56a-4bc6-a73f-4bda0b2792e7",
                "ip_internal_start": "192.168.10.1" }
        print data["customer_name"], "name"
        print data["vdc_id"], "vdc id"
        print data["ip_internal_start"], "ip internal start"
        cluster = getVcenterVcloudDetail("test")
        vcloud_token = create_sessions(cluster)
        vapp, err = vapp_id(vcloud_token, data["vdc_id"])
        print "i"
        if not err:
            print "f"
            vm_id,err = vmID(vcloud_token,vapp)
            print vm_id,"vm"
            if not err:
                vm,err = vm_connect_network(vcloud_token, vm_id, data["customer_name"], data["ip_internal_start"])
                if not err:
                    print "create org_vdc_network success"
                    dict = {"header": header,
                            "customer_name": data["customer_name"],
                            "ip_internal_start": data["ip_internal_start"],
                            "message": "You connect network vapp success already."}
                    return json.dumps(dict)
                else:
                    dict = {"message": "You can not connect network vapp."}
                    return json.dumps(dict)
            else:
                dict = {"message": "You can not get vm_id."}
                return json.dumps(dict)
        else:
            dict = {"message": "You can not get vapp."}
            return json.dumps(dict)

    except Exception as e:
        print e
        dict = {"message": "You can not connect network vapp."}
        return json.dumps(dict)


# def all_network():
#     try:
#         # header = request.headers
#         header = {"BD": "flexpod"}
#         # data = request.json
#         ip_gateway = "192.168.0.254"
#         netmask = "255.255.255.0"
#         data = {"customer_name" : "Obesity",
#                 "vdc_id" : "82f1f86a-a56a-4bc6-a73f-4bda0b2792e7",
#                 "ip_internal_start" : "192.168.10.1",
#                 "ip_internal_end" : "192.168.10.253",
#                 "ip_external_start": "203.150.67.112",
#                 "ip_external_end": "203.150.67.113"
#                 }
#         # print data["customer_name"], "name"
#         # print data["vdc_id"], "vdc id"
#         # print data["ip_internal_start"], "ip internal start"
#         # print data["ip_internal_end"], "ip_internal_end"
#         # print data["ip_external_start"], "ip externaml start"
#         # print data["ip_external_end"], "ip external end"
#         cluster = getVcenterVcloudDetail("test")
#         vcloud_token = create_sessions_network(cluster)
#         # print vcloud_token, "debug"
#         external_network, err = external_network_id(vcloud_token)
#         # print external_network,"test"
#         edge, err = create_edge(vcloud_token, data["vdc_id"], data["ip_external_start"], data["ip_external_end"], external_network, data["customer_name"])
#         print edge
#         # print "create edge success"
#         # time.sleep(150)
#         gateway_id, err = edgeGateways(vcloud_token, data["vdc_id"])
#         # print gateway_id,"gateway id"gateway_id,err =  edgeGateways(vcloud_token,vdc_id)
#
#         print gateway_id
#         org_vdc, err = org_vdc_network(vcloud_token, data["vdc_id"], data["ip_internal_start"], data["ip_internal_end"], gateway_id, data["customer_name"])
#         print org_vdc
#
#         # time.sleep(30)
#         id_network, err = org_vdc_network_id(vcloud_token)
#         print id_network
#         # print "create org vdc success"
#         mod_nat, err = modify_nat(vcloud_token, gateway_id, data["ip_external_end"], data["ip_internal_start"], id_network)
#         print mod_nat
#         # print "create nat success"
#         vapp, err = vapp_id(vcloud_token, data["vdc_id"])
#         add_network = add_network_vapp(vcloud_token, vapp, data["customer_name"], ip_gateway, netmask, data["ip_internal_start"],
#                          data["ip_internal_end"], id_network)
#         print add_network
#
#         vm_id, err = vmID(vcloud_token, vapp)
#         print vm_id, "test id vm"
#         # time.sleep(10)
#         vm_connect, err = vm_connect_network(vcloud_token, vm_id, data["customer_name"], data["ip_internal_start"])
#         print vm_connect
#
#         return "Setting NSX SUCCESS"
#     except Exception as e:
#         print e
#         # dict = {"ERROR"}
#         return "Setting NSX ERROR"


# def all_network():
# # try:
#     # header = request.headers
#     header = {"BD": "flexpod"}
#     # data = request.json
#     ip_gateway = "192.168.0.254"
#     netmask = "255.255.255.0"
#     data = {"customer_name" : "lup_wacc_Cust",
#             "vdc_id" : "eca56070-bd60-4f96-85c1-cb2c9778be02",
#             "ip_internal_start" : "192.168.10.1",
#             "ip_internal_end" : "192.168.10.253",
#             "ip_external_start": "203.150.67.112",
#             "ip_external_end": "203.150.67.113"
#             }
#     # print data["customer_name"], "name"
#     # print data["vdc_id"], "vdc id"
#     # print data["ip_internal_start"], "ip internal start"
#     # print data["ip_internal_end"], "ip_internal_end"
#     # print data["ip_external_start"], "ip externaml start"
#     # print data["ip_external_end"], "ip external end"
#     cluster = getVcenterVcloudDetail("test")
#     vcloud_token = create_sessions_network(cluster)
#     # print vcloud_token, "debug"
#     external_network, err = external_network_id(vcloud_token)
#     if not err:
#         gateway_data, err = create_edge(vcloud_token, data["vdc_id"], data["ip_external_start"], data["ip_external_end"], external_network, data["customer_name"])
#         #--------------
#         print "gate ERROR???????????????????????"
#         if not err:
#             task_edge_url = gateway_data[0]
#             gateway_url = gateway_data[1]
#             gateway_id = gateway_url.split('/')[-1]
#             task_edge_status = check_task_status(task_edge_url,vcloud_token)
#
#             print "create edge success"
#             if task_edge_status:
#                 org,err = org_vdc_network(vcloud_token, data["vdc_id"], data["ip_internal_start"], data["ip_internal_end"], gateway_id, data["customer_name"])
#                 if not err:
#                     # print org,"data org"
#                     print org[0],"test1"
#                     print org[1],"test2"
#                     # return "D"
#                     task_ovn_url,ovn_id = org[0], org[1].split('/')[-1]
#                     task_ovn_status = check_task_status(task_ovn_url, vcloud_token)
#                     print task_ovn_status,"task ovn url"
#                     # print ovn_id,"ovn id"
#                     # return "ffL"
#                     if task_ovn_status:
#                         print "create org vdc success"
#                         nat,err = modify_nat(vcloud_token, gateway_id, data["ip_external_end"], data["ip_internal_start"], ovn_id)
#                         if not err:
#                             print "create nat success"
#                             # return "GG"
#                             vapp, err = vapp_id(vcloud_token, data["vdc_id"])
#                             if not err:
#                                 network_vapp,err = add_network_vapp(vcloud_token, vapp, data["customer_name"], ip_gateway, netmask, data["ip_internal_start"],data["ip_internal_end"], ovn_id)
#                                 if not err:
#                                     print "network vapp success"
#                                     # task_anv_url = network_vapp.split('/')[-1]
#                                     # print task_anv_url,"test task_anv_url"
#                                     # task_anv_url = "https://"+task_anv_url
#                                     task_anv_status = check_task_status(network_vapp, vcloud_token)
#                                     print "check task success"
#                                     # return "Savee overload"
#                                     vm_id, err = vmID(vcloud_token, vapp)
#                                     if not err:
#                                         print vm_id, "test id vm"
#                     #                 time.sleep(10)
#                                         vm,err = vm_connect_network(vcloud_token, vm_id, data["customer_name"], data["ip_internal_start"])
#                                         if not err:
#                                             print "create vm_connect_network success"
#                                             guest, err = guestCustomization(vcloud_token, vm_id, data["customer_name"])
#                                             if not err:
#                                                 print "Enable Guest"
#                                                 dict = {"header": header,
#                                                         "customer_name": data["customer_name"],
#                                                         "ip_internal_start": data["ip_internal_start"],
#                                                         "ip_external_end": data["ip_external_end"],
#                                                         "message": "You connect network vapp success already."}
#                                                 return json.dumps(dict)
#                                             else:
#                                                 dict = {"message": "You can not enable guest customize."}
#                                         else:
#                                             dict = {"message": "You can not connect network vm."}
#                                             return json.dumps(dict)
#                                     else:
#                                         dict = {"message": "You can not get vm_id."}
#                                         return json.dumps(dict)
#                                 else:
#                                     dict = {"message": "You can not connect network vapp."}
#                                 return json.dumps(dict)
#                             else:
#                                 dict = {"message": "You can not connect vapp_id."}
#                             return json.dumps(dict)
#                         else:
#                             dict = {"message": "You can not connect Nat."}
#                             return json.dumps(dict)
#
#                     else:
#                         dict = {"message": "You can not connect org_vdc_network_id."}
#                     return json.dumps(dict)
#                 else:
#                     dict = {"message": "You can not connect org_vdc_network."}
#                 return json.dumps(dict)
#             else:
#                 dict = {"message": "You can not get gateway id."}
#                 return json.dumps(dict)
#         else:
#             dict = {"message": "You can not create edge."}
#             return json.dumps(dict)
#     else:
#         dict = {"message": "You can not get external network."}
#         return json.dumps(dict)
#
#     # except Exception as e:
#     #     print e
#     #     dict = {"message": "Error creating network."}
#     #     return json.dumps(dict)
#     #


def nsx_network():
    data = request.json
    vcloud_data = data
    front_data = data
    condition, return_data = all_network(vcloud_data, front_data)
    # condition = False
    if condition is True:
        return json.dumps("success")
    else:
        return json.dumps("Error")


def all_vlan():
    try:
        # header = request.headers
        header = {"BD": "flexpod"}
        # data = request.json
        # ip_gateway = "192.168.0.254"
        # netmask = "255.255.255.0"
        data = {"customer_name": "Obesity",
                "create_new_vlanid": "2029",
                "create_org": "AIS",
                "interface_one": "AIS_eth00",
                "interface_two": "AIS_eth01",
                }
        print data["customer_name"],"customer_name"
        print data["create_org"],"create_org"
        print data["create_new_vlanid"],"create_new_vlanid"
        print data["interface_one"],"interface_one"
        print data["interface_two"],"interface_two"
        hostname = '10.20.200.20'
        port = 22
        username = 'sdivlan'
        password = '7uJm,ki*'
        real_vlan_name = "{}_{}".format(data["customer_name"], data["create_new_vlanid"])
        # create_new_name_vlan = "TWacc-88888888"
        # create_new_vlanid = "2029"
        # create_org = "AIS"
        # interface_one = "AIS_eth00"
        # interface_two = "AIS_eth01"
        shell_fi = session_ssh(hostname, port, username, password)
        org_fi,err = list_name_org(shell_fi, data["create_org"])
        print org_fi,"oil test"
        if not err:
            print "create vlan after check by name because you don't have vlan."
            com, com1 = command(shell_fi, real_vlan_name, data["create_new_vlanid"])
            if com1 == "create":
                create_vlan(shell_fi, real_vlan_name, data["create_new_vlanid"])
                print "next to add vnic."
            else:
                dict = {"message" : "You can't use this name."}
                print "You can't use this name."
                return json.dumps(dict)
        org1,err = org(shell_fi, org_fi, real_vlan_name,data["interface_one"],data["interface_two"])
        if not err:
            dict = {"header": header,
                    "customer_name": real_vlan_name,
                    "create_new_vlanid" : data["create_new_vlanid"],
                    "interface_one" : data["interface_one"],
                    "interface_two" : data["interface_two"]
                    }
            return json.dumps(dict)
        else:
            dict = {"message" : "You can't create interface."}
            return json.dumps(dict)
    except Exception as e:
        print e
        dict = {"message": "You can not connect network vapp."}
        return json.dumps(dict)


#  ---------------------------------------------------- Compute --------------------------------------------------------


def comparisonBlade():
    result_data = show_assoc()
    # print result_data, "Yes"
    return json.dumps("Yes")

