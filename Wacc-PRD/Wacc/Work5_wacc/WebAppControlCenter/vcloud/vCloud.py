import requests
from flask import Flask, json, request, jsonify, session, abort, Response
# Import modules
import xml.etree.cElementTree as ET
from xmljson import badgerfish as bf
import json
import time
import urllib3
import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import pymysql
import os
from sqlalchemy import create_engine
from yaml import load
import math
import base64

pymysql.install_as_MySQLdb()

urllib3.disable_warnings()


data_vcloud = load(open("WebAppControlCenter\\vcloud\data_vcloud.yaml"))

# data_vcloud = load(open("/home/sdiadmin/Web-app/wacc-app/WebAppControlCenter/vcloud/data_vcloud.yaml"))
# print data_vcloud


def json_response(messages=None, status=None, headers=None):
    """

    :rtype: object
    """
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

def getVcenterVcloudDetail(cluster):
    vcloud_ip = data_vcloud["user"]["vcloud_ip"]
    username_vcloud = data_vcloud["user"]["username"]
    password_vcloud = data_vcloud["user"]["password"]
    dict_data = {"vcloud_ip": vcloud_ip,
                "vcloud_username": username_vcloud,
                "vcloud_password":password_vcloud}
    return dict_data

   # return json_response({"messages": list_data}, 200)



def create_sessions(hostname,username,password):
    url = "https://"+hostname+"/api/sessions"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'Authorization': "Basic "+ base64.b64encode(username+":"+password)
        }

    response = requests.request("POST", url, verify=False, data=payload, headers=headers)
    # print type(response.text)
    try:
        if response.status_code == 200:
            print response
            doc = ET.fromstring(response.text.encode('utf-8'))
            jsonStr = json.dumps(bf.data(doc))
            jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
            y = json.loads(jsonStr)
            # print y,"\nsessions"
            # print(response.text)
            # print response.headers.get("x-vcloud-authorization")
            id_sess = response.headers.get("x-vcloud-authorization")
            return id_sess
            # dbTest(id_sess)
    except Exception as e:
        print response


def get_org(cluster,vcloud_token):

    url = "https://"+cluster["vcloud_ip"]+"/api/org"
    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<vmext:VMWProviderVdcParams\r\n   xmlns:vmext=\"http://www.vmware.com/vcloud/extension/v1.5\"\r\n   xmlns:vcloud=\"http://www.vmware.com/vcloud/v1.5\"\r\n   name=\"TEST-vdc\">\r\n   <vcloud:Description>TEST</vcloud:Description>\r\n   <vmext:ResourcePoolRefs>\r\n      <vmext:VimObjectRef>\r\n         <vmext:VimServerRef\r\n            href=\"https://vcloud.example.com/api/admin/extension/vimServer/9\" />\r\n         <vmext:MoRef>resgroup-195</vmext:MoRef>\r\n         <vmext:VimObjectType>RESOURCE_POOL</vmext:VimObjectType>\r\n      </vmext:VimObjectRef>\r\n   </vmext:ResourcePoolRefs>\r\n    <StorageProfiles>\r\n        <ProviderVdcStorageProfile href=\"https://10.10.21.155/api/admin/pvdcStorageProfile/c68c6439-c2ac-4f0e-9331-0a586c970734\" id=\"urn:vcloud:providervdcstorageprofile:c68c6439-c2ac-4f0e-9331-0a586c970734\" name=\"BTT_UCSD_POC_PUB_02\" type=\"application/vnd.vmware.admin.pvdcStorageProfile+xml\"/>\r\n    </StorageProfiles>\r\n        <IsEnabled>true</IsEnabled>\r\n    <NetworkPoolReferences>\r\n        <NetworkPoolReference href=\"https://10.10.21.155/api/admin/extension/networkPool/f48f0da4-df9f-4339-aede-f31b8de65cea\" />\r\n    </NetworkPoolReferences>\r\n    \r\n   <vmext:VimServer\r\n      href=\"https://vcloud.example.com/api/admin/extension/vimServer/9\" />\r\n   <vmext:StorageProfile>Gold</vmext:StorageProfile>\r\n</vmext:VMWProviderVdcParams>"
    headers = {
        'Content-Type': "application/vnd.vmware.admin.createVdcParams+xml",
        'x-vcloud-authorization': vcloud_token,
        'Accept': "application/*+xml;version=31.0"
        }


    try:
        response = requests.request("GET", url, verify=False, data=payload, headers=headers)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        org_list = json.loads(jsonStr)
        list_data = []
        if org_list["OrgList"]["Org"] == {}:
            print "Never have org"
            return None, True
        elif org_list["OrgList"]["Org"] != {}:
            print "start list org"
            for k in range(len(org_list["OrgList"]["Org"])):
                dict_data = {"org_name": org_list["OrgList"]["Org"][k]["@name"],
                             "org_url": org_list["OrgList"]["Org"][k]["@href"]}
                list_data.append(dict_data)
            # print "start\n", list_data, "\nend"
        return list_data, True
    except Exception as e:
        print 'get_org error',e
        return None, False


def get_vdc(cluster,vcloud_token,org_id):
# def check_name_vdc():
    url = "https://%s/api/org/%s" %(cluster['vcloud_ip'],org_id)
    headers = {
        'x-vcloud-authorization': vcloud_token,
        'Accept': "application/*+xml;version=31.0",
        'Content-Type': "application/vnd.vmware.admin.user+xml"
    }
    try :
        response = requests.request("GET", url, verify=False, headers=headers)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        vdc_objs = json.loads(jsonStr)
        # vdc_list = []
        if vdc_objs["Org"]["Link"] == {}:
            print "Never have vdc list"
            return None, False
        elif vdc_objs["Org"]["Link"] != {}:
            for i in range(len(vdc_objs["Org"]["Link"])):
                vdc_list = []
                if vdc_objs["Org"]["Link"][i]["@type"] == "application/vnd.vmware.vcloud.vdc+xml":
                    vdc_list.append(vdc_objs["Org"]["Link"][i]["@name"])
            return vdc_list, False
    except Exception as e:
        print e
    return None,True


def create_org_on_vcloud(cluster,vcloud_token,customer_name):
    org_list,err = get_org(cluster,vcloud_token)
    if not err:
        print "cannot get org list"
        return None, True
    org_name_list = []
    for org in org_list:
        org_name_list.append(org["org_name"])
    # print org_name_list, "list org"
    if org_name_list == None or customer_name not in org_name_list:
        print "You can use this name"

        url = "https://%s/api/admin/orgs" %(cluster["vcloud_ip"])
        payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<AdminOrg\r\n" \
                  "   xmlns=\"http://www.vmware.com/vcloud/v1.5\"\r\n  " \
                  " name=\""+customer_name+"\"\r\n   " \
                  "type=\"application/vnd.vmware.admin.organization+xml\">\r\n   " \
                "<Description></Description>\r\n   " \
                "<FullName>"+customer_name+"</FullName>\r\n   " \
                "<IsEnabled>true</IsEnabled>\r\n   " \
                "<Settings>\r\n      " \
                    "<OrgGeneralSettings>\r\n         " \
                        "<CanPublishCatalogs>false</CanPublishCatalogs>\r\n      " \
                        "<CanPublishExternally>false</CanPublishExternally>\r\n         " \
                        "<CanSubscribe>true</CanSubscribe>\r\n        " \
                        "<DeployedVMQuota>0</DeployedVMQuota>\r\n         " \
                        "<StoredVmQuota>0</StoredVmQuota>\r\n         " \
                        "<UseServerBootSequence>false</UseServerBootSequence>\r\n         " \
                        "<DelayAfterPowerOnSeconds>0</DelayAfterPowerOnSeconds>\r\n         \r\n     " \
                    "</OrgGeneralSettings>" \
                    "<OrgLdapSettings>" \
                        "<OrgLdapMode>SYSTEM</OrgLdapMode>" \
                        "<CustomUsersOu />" \
                    "</OrgLdapSettings>" \
                    "<OrgEmailSettings>" \
                        "<IsDefaultSmtpServer>true</IsDefaultSmtpServer>" \
                        "<IsDefaultOrgEmail>true</IsDefaultOrgEmail>" \
                        "<FromEmailAddress />" \
                        "<DefaultSubjectPrefix />" \
                        "<IsAlertEmailToAllAdmins>true</IsAlertEmailToAllAdmins>" \
                    "</OrgEmailSettings>" \
                    "</Settings>" \
                "</AdminOrg>"
        headers = {
            'Content-Type': "application/vnd.vmware.admin.organization+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
            }
        try:
            response = requests.request("POST", url, verify=False, data=payload, headers=headers)
            doc = ET.fromstring(response.text.encode('utf-8'))
            org_id = doc.attrib.get('id')[15:]
            url_org = "https://%s/cloud/org/%s/" %(cluster['vcloud_ip'],customer_name)
            dict_data = {
                            "org_name" : customer_name,
                            "org_url" : url_org ,
                            "org_id" : org_id,
                        }
            return dict_data, False

        except Exception as e:
            print response
            print e
            return None, True
    else:
        print "you have this name already"
        return None, True


def create_vdc_on_vcloud(cluster,vcloud_token,org_id,customer_name,zone, cpu, mem, disk):
    vdc_list,err_vdc = get_vdc(cluster,vcloud_token,org_id)
    if err_vdc:
        print "cannot get vdc"
        return None,True
    print "vdc_list>>",vdc_list
    vdc_name = "vdc_%s_%s"%(customer_name,zone)
    if vdc_list == {} or customer_name not in vdc_list:
    # if vdc_name not in vdc_list:
        cpu = int(math.ceil(int(cpu) * (1.2 * 2.6)))
        mem = int(math.ceil(int(mem) * 1.2))
        storage = int(int(disk) + math.ceil(int(mem)))
        limit_cpu = data_vcloud["spac"]["limit_cpu"]
        limit_mem = data_vcloud["spac"]["limit_mem"]
        AllocationModel = data_vcloud["spac"]["AllocationModel"]

        url = "https://10.10.21.155/api/admin/org/" + org_id + "/vdcsparams"

        payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                  "<CreateVdcParams name=\""+vdc_name+"\"   xmlns=\"http://www.vmware.com/vcloud/v1.5\">" \
                  "<Description></Description>" \
                "<AllocationModel>"+AllocationModel+"</AllocationModel>" \
                "<ComputeCapacity>" \
                    "<Cpu>" \
                        "<Units>MHz</Units>" \
                        "<Allocated>"+str(cpu)+"</Allocated>" \
                        "<Limit>"+str(limit_cpu)+"</Limit>" \
                    "</Cpu>" \
                    "<Memory>" \
                        "<Units>MB</Units>" \
                        "<Allocated>"+str(mem)+"</Allocated>" \
                        "<Limit>"+str(limit_mem)+"</Limit>" \
                    "</Memory>" \
                "</ComputeCapacity>" \
                "<NicQuota>0</NicQuota>" \
                "<NetworkQuota>1</NetworkQuota>" \
                "<VdcStorageProfile>" \
                    "<Enabled>true</Enabled>" \
                    "<Units>MB</Units>" \
                    "<Limit>102400</Limit>" \
                    "<Default>true</Default>" \
                    "<ProviderVdcStorageProfile href=\"https://10.10.21.155/api/admin/pvdcStorageProfile/c68c6439-c2ac-4f0e-9331-0a586c970734\" />" \
                "</VdcStorageProfile>" \
                "<ResourceGuaranteedMemory>0.2</ResourceGuaranteedMemory>" \
                "<ResourceGuaranteedCpu>0.0</ResourceGuaranteedCpu>" \
                "<VCpuInMhz>2048</VCpuInMhz>" \
                "<IsThinProvision>true</IsThinProvision>" \
                "<NetworkPoolReference href=\"https://10.10.21.155/api/admin/extension/networkPool/f48f0da4-df9f-4339-aede-f31b8de65cea\"/>" \
                "<ProviderVdcReference  name=\"Main Provider\"  " \
                "href=\"https://10.10.21.155/api/admin/providervdc/f1c560de-9ba4-4d9d-b6df-4069556fe9f5\" />" \
                "<UsesFastProvisioning>false</UsesFastProvisioning>" \
            "</CreateVdcParams>"

        headers = {
            'Accept': "application/*+xml;version=31.0",
            'x-vcloud-authorization': vcloud_token
        }

        response = requests.request("POST", url, verify=False, data=payload, headers=headers)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        y = json.loads(jsonStr)
        # print "vdc data>>",y
        dict_data = {"vdc_name": vdc_name,
                     "vdc_id": y['AdminVdc']['@id'].split(':')[3]}
        return dict_data, False

    else:
        print "you can use this name"


def getOrgRoleID(hostname,role_id, vcloud_token):
    print "...Getting Admin Role ID"
    print hostname
    print role_id
    print vcloud_token
    url = "https://%s/api/admin/org/%s"%(hostname,role_id)
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': "%s" % vcloud_token
    }
    print "bug"
    resp = requests.request(
        "GET",
        url,
        verify=False,
        headers=headers
    )
    print resp
    raw_list_data = resp.text.split('<RoleReferences>')[1].splitlines()[0:-2]
    print raw_list_data
    role_catalog = {}
    for item in raw_list_data:
        if item != '':
            role_catalog[item.split('"')[3]] = item.split('"')[1]
    role_id = role_catalog['Organization Administrator'].split('/').pop()
    print "ROLE ID : " ,role_id
    return role_id


def vmsList(vcloud_token):
    # vcloud_ip = "10.10.21.155"
    # username = "administrator@system"
    # password = "6yHnmju&"
    # vcloud_token =  create_sessions(cluster["vcloud_ip"],cluster["vcloud_username"],cluster["vcloud_password"])
    url = "https://10.10.21.155/api/admin/extension/vimServer/e0d21e6e-1beb-4f8c-bd75-2d3cb891facb/vmsList"

    payload = ""
    headers = {
        'Content-Type': "application/vnd.vmware.vcloud.owner+xml",
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
    }

    response = requests.request("GET", url, verify=False, data=payload, headers=headers)
    try:
        # print(response.text)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/extension/v1.5}", "")
        vm_objs = json.loads(jsonStr)
        vm_list = []
        list_vm = []
        list_vm = []
        # print vm_objs["VmObjectRefsList"]["VmObjectRef"][0]
        # print vm_objs["VmObjectRefsList"]["VmObjectRef"][0]["@name"]
        if vm_objs["VmObjectRefsList"]["VmObjectRef"] == {}:
            print "Never have vapp user"
            return None, False
        elif vm_objs["VmObjectRefsList"]["VmObjectRef"] != {}:
            for k in range(len(vm_objs["VmObjectRefsList"]["VmObjectRef"])):
                vm_test = vm_objs["VmObjectRefsList"]["VmObjectRef"][k]["@name"]
                # print vm_test
                vm_list.append(vm_test)
            for g in vm_list:
                print g
                list_vm.append(g)
            return list_vm, True
    except Exception as e:
        print e
        return None, False


def cheack_name_user(vcloud_token, org_id):
    url = "https://10.10.21.155/api/admin/org/" + org_id
    # Debug
    print "Check name url:", url
    headers = {
        'Content-Type': "application/vnd.vmware.admin.user+xml",
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
    }
    # Debug
    print "Check headers :", headers
    response = requests.request("GET", url, verify=False, headers=headers)
    try:
        # Debug
        # print "Check response :", response.text
        # print response.text,"\nXML"
        # print "test"
        doc = ET.fromstring(response.text.encode('utf-8'))
        # Debug
        # print "Check xml to json :", doc
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        user_list = json.loads(jsonStr)
        # Debug
        # print "Check user list :", user_list
        # print "------------------\n",user_list,"\nuser list"
        user_data = []

        if user_list["AdminOrg"]["Users"] == {}:
            print "true"
            return None, True
        elif user_list["AdminOrg"]["Users"] != {}:
            print "false"
            for k in range(len(user_list["AdminOrg"]["Users"])):
                # print user_list["AdminOrg"]["Users"]["UserReference"],"de"
                user_data.append(user_list["AdminOrg"]["Users"]["UserReference"][k]["@name"])
        return user_data, True
    except Exception as e:
        print e
        print "kkk"
        return None, False


def createvAppUser(vapp_username, vapp_user_password, hostname,vcloud_token,org_id):
    user_list, err = cheack_name_user(vcloud_token, org_id)
    if not err:
        print "cannot get user list"
        return None, True
    # print "user_list:",user_list
    if user_list == None or vapp_username not in user_list:
        print "You can use this name"

        switcher = True
        if switcher:
            admin_role_id = getOrgRoleID(hostname,org_id,vcloud_token)
            print admin_role_id,"role id"

            payload = '<?xml version="1.0" encoding="UTF-8"?>\n'\
            '<User\n'\
               'xmlns="http://www.vmware.com/vcloud/v1.5"\n'\
               'name="%s">\n'\
               '<FullName>Example User Full Name</FullName>\n'\
               '<EmailAddress>user@example.com</EmailAddress>\n'\
               '<IsEnabled>true</IsEnabled>\n'\
               '<Role\n'\
                  'href="https://10.10.21.155/api/admin/role/%s" />\n'\
               '<Password>%s</Password>\n'\
               '<GroupReferences/>\n'\
            '</User>\n'%(vapp_username, admin_role_id,vapp_user_password)

            url = "https://10.10.21.155/api/admin/org/%s/users" % (org_id)
            print "DEB Create user : " ,url

            headers = {
                'Accept': "application/*+xml;version=31.0",
                'x-vcloud-authorization': "%s" % vcloud_token
            }

            print vcloud_token
            print "test"
            response = requests.request("POST", url, data=payload, headers=headers, verify=False)
            try:
                doc = ET.fromstring(response.text.encode('utf-8'))
                jsonStr = json.dumps(bf.data(doc))
                jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
                user = json.loads(jsonStr)
                print "usre data>>", user
                print response.status_code
                dict_data = {
                    "user_name": vapp_username,
                    "vapp_user_password": vapp_user_password,
                }
                return dict_data, False
            except Exception as e:
                print response
                print e
                return None, True
    else:
        print "You used this name already"


def add_vm_to_cloud(cluster, vcloud_token, vm_name, vdc_id, vapp_name, vm_id):
    print "dubugg"
    vm_list,err = vmsList(vcloud_token)
    if not err:
        print "cannot get vm list"
        return None, True
    print vm_list, "vm list"
    for list in vm_list:
        print list
        if vm_list == {} or vm_name not in list:
        # if vm_name == list:
            time.sleep(30)
            url = "https://10.10.21.155/api/admin/extension/vimServer/e0d21e6e-1beb-4f8c-bd75-2d3cb891facb/importVmAsVApp"
            payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<ImportVmAsVAppParams\n" \
                      "xmlns=\"http://www.vmware.com/vcloud/extension/v1.5\"\r\n\tname=\""+vapp_name+"\"\t" \
                      "sourceMove=\"true\">\r\n<VmName>"+vm_name+"</VmName>\r\n <VmMoRef>"+vm_id+"</VmMoRef>" \
                      "\n<Vdc href=\"https://10.10.21.155/api/admin/vdc/"+vdc_id+"\" />\n" \
                      "</ImportVmAsVAppParams>\r\n"
            headers = {
                'Content-Type': "application/vnd.vmware.admin.importVmAsVAppParams+xml",
                'Accept': "application/*+xml;version=31.0",
                'x-vcloud-authorization': vcloud_token,
            }
            response = requests.request("POST", url, verify=False, data=payload, headers=headers)
            # try:
            doc = ET.fromstring(response.text.encode('utf-8'))
            jsonStr = json.dumps(bf.data(doc))
            jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
            vapp = json.loads(jsonStr)
            # print "vapp data>>", vapp
            print response.status_code
            dict_data = {
                "vm_name": vm_name,
                "vm_id": vm_id,
            }
            return dict_data, False
            # except Exception as e:
            #     print response
            #     print e
            #     return None, True
        else:
            print "Don't have this vm name"
    return None, True


def mainVcloud(data):
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
        print "test_vdc"
        vdc,vdc_err = create_vdc_on_vcloud(cluster, vcloud_token, org['org_id'], customer_name, zone, cpu, mem, disk)
        print vdc["vdc_id"]
        print vdc_err
        if not vdc_err:
            print "do more"
            vapp,vapp_err = add_vm_to_cloud(cluster, vcloud_token, vm_name, vdc["vdc_id"], customer_name, vm_id)
            print vapp_err
            if not vapp_err:
                print "do it"
                result_dict = {}
                result_dict = org.copy()
                result_dict.update(vdc)
                result_dict.update(vapp)
                user, user_err = createvAppUser(vapp_username, vapp_user_password, cluster["vcloud_ip"], vcloud_token,
                                                org['org_id'])
                if not user_err:
                    print "Create user vapp"
                    result_dict.update(user)
                    return True, result_dict
                else:
                    return False, {"CreateError": "Can't create vapp user"}
            else:
                print "can not create vApp"
                return False, {"CreateError": "Can't create vApp"}
        else:
            print "cannot create vdc"
            return False, {"CreateError": "Can't create vdc"}
        # return False, {"Create Organize": "Can't create organize"}
    else:
        print "error create organize"
        return False, {"CreateError": "Can't create organize"}
        # return json_response({"message":"error to create organize"},400)
        # return "error to create organize"

# cluster = getVcenterVcloudDetail("test")
# vcloud_token =  create_sessions(cluster["vcloud_ip"],cluster["vcloud_username"],cluster["vcloud_password"])
#
# print vcloud_token
