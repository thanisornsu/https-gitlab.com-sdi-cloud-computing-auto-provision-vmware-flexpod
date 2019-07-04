from flask import Flask, Response, json, request, abort, make_response, jsonify
import requests
from yaml import load

from ..provisioning.Provisioning import vmName, deployMachine, deploySpecialMachine, getStorage
from ..vcloud.vCloud import mainVcloud
from ..storage.createStorage import mainBuildStorage, getAggregate, checkVserver, checkVolume

import urllib3
urllib3.disable_warnings()


def detailData():
    vm_data = vmName()
    if vm_data == "This vm name has already in use":
        return "This vm name has already in use"
    else:
        return vm_data


def storageData():
    storage_data = getStorage()
    return storage_data


# def createOther(condition_case):
#     dict_result = {}
#     if condition_case == True:
#         return_case, condition, return_detail = getVcenterVcloudDetail()
#         dict_result["username"] = return_detail["username_vcloud"]
#         dict_result["password"] = return_detail["password_vcloud"]
#         dict_result["vcloud_ip"] = return_detail["vcloud_ip"]
#         # return return_detail
#         if condition == True:
#             return_case, condition, return_org = createOrgOnVcloud()
#             dict_result["org_name"] = return_org["Org_name"]
#             dict_result["org_url"] = return_org["Org_url"]
#             dict_result["org_description"] = return_org["Org_description"]
#             dict_result["customer_name"] = return_org["customer_name"]
#             dict_result["company_name"] = return_org["company_name"]
#             return return_case, dict_result
#         else:
#             return "Can't create org", dict_result
#     else:
#         return "Doesn't have vcloud data", dict_result
#     # return "vCenter ready"
#

def createOther(condition_case, data):
    dict_result = {}
    if condition_case is True:
        condition, return_data = mainVcloud(data)
        if condition is True:
            # print condition
            # print return_data
            dict_result["orgName"] = return_data["org_name"]
            dict_result["orgUrl"] = return_data["org_url"]
            dict_result["orgId"] = return_data["org_id"]
            dict_result["vmName"] = return_data["vm_name"]
            dict_result["vmId"] = return_data["vm_id"]
            dict_result["vApp_username"] = return_data["user_name"]
            dict_result["vApp_password"] = return_data["vapp_user_password"]
            return True, dict_result
        else:
            return False, return_data
    else:
        return False, dict_result
    # return "vCenter ready", dict_result


def sendData(receive_data):
    dict_result = {}
    front_data = receive_data
    if front_data.has_key("templateName"):
        get_template = front_data["templateName"]
        with open('WebAppControlCenter\driver\config.yaml') as f:
        # with open('/home/sdiadmin/Web-app/wacc-app/WebAppControlCenter/driver/config.yaml') as f:
            yaml_data = load(f)
            template_name = yaml_data["template"]
            for each_template in template_name:
                if each_template["template_name"] == get_template:
                    template_id = each_template["template_id"]
                    template_cpu = each_template["CPU"]
                    template_mem = each_template["Memory"]
                    template_disk = each_template["Disk"]
                    front_data["templateId"] = template_id
                    front_data["cpuCount"] = template_cpu
                    front_data["memorySize"] = template_mem
                    front_data["diskCapacity"] = template_disk
                    # deployMachine(receive_data)
                    condition, return_data = deployMachine(front_data)
                    if condition is True:
                        print condition, "Template 84"
                        return_case, dict_result = createOther(condition, return_data)
                        dict_result["vmName"] = return_data["name"]
                        dict_result["vmId"] = return_data["vmId"]
                        dict_result["storage"] = return_data["storage"]
                        dict_result["storageType"] = return_data["storageType"]
                        dict_result["networkName"] = return_data["networkName"]
                        dict_result["templateName"] = each_template["template_name"]
                        dict_result["cpu"] = each_template["CPU"]
                        dict_result["memory"] = each_template["Memory"]
                        dict_result["disk"] = each_template["Disk"]
                        return condition, dict_result
                    else:
                        print condition, "Template 94"
                        return_data["Result"] = "Doesn't Vm to deploy (template)"
                        return condition, return_data
                else:
                    pass
    else:
        # deploySpecialMachine(receive_data)
        condition, return_data = deploySpecialMachine(front_data)
        # print return_data
        if condition is True:
            print condition, "Config 109"
            # print return_data
            return_case, dict_result = createOther(condition, return_data)
            dict_result["vmName"] = return_data["name"]
            dict_result["vmId"] = return_data["vmId"]
            dict_result["serviceOs"] = return_data["serviceOs"]
            dict_result["cpuCount"] = return_data["cpuCount"]
            dict_result["memorySize"] = return_data["memorySize"]
            dict_result["diskCapacity"] = return_data["diskCapacity"]
            dict_result["datastore"] = return_data["datastore"]
            dict_result["network"] = return_data["network"]
            dict_result["networkType"] = return_data["networkType"]
            return condition, dict_result
        else:
            print condition, "Config 121"
            return_data["Result"] = "Doesn't Vm to deploy"
            return condition, return_data


def vServerName():
    v_name = "INET_TEMP_SDI"
    # vserver_name, condition = checkVserver(v_name)
    vserver_name, condition = checkVserver()
    return vserver_name


def volumeName():
    volume_name, condition = checkVolume()
    return volume_name


def aggregateValue():
    aggregate = getAggregate()
    return aggregate


def createMainVolume(frontend_data):
    all_data = frontend_data
    build = mainBuildStorage(all_data)
    return build

