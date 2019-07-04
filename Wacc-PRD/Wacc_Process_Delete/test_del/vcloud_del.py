import json
import requests
from flask import Flask, json, request, jsonify, session, abort, Response

import xml.etree.cElementTree as ET
from xmljson import badgerfish as bf
import time
import urllib3
from yaml import load
import math
import base64


urllib3.disable_warnings()

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

def create_sessions(hostname,username,password):
    url = "https://"+hostname+"/api/sessions"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'Authorization': "Basic "+ base64.b64encode(username+":"+password)
        }
    # print username , password

    response = requests.request("POST", url, verify=False, data=payload, headers=headers)
    print type(response.text)
    try:
        if response.status_code == 200:
            # print response
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


# First
# เป็นฟังก์ชันแรกที่ต้องทำใน Process Delete VM ก็คือ ฟังก์ชันการ ถอดขา Network ในเครื่อง VM
def disconnected_network_vm(vcloud_token, vm_id, hostname):

    url = "https://"+hostname+"/api/vApp/"+vm_id+"/networkConnectionSection"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<NetworkConnectionSection \n  " \
              " type=\"application/vnd.vmware.vcloud.networkConnectionSection+xml\"\n  " \
              " xmlns=\"http://www.vmware.com/vcloud/v1.5\"\n   " \
              "xmlns:ovf=\"http://schemas.dmtf.org/ovf/envelope/1\">\n   " \
              "<ovf:Info>Firewall allows access to this address.</ovf:Info>\n " \
              "  <PrimaryNetworkConnectionIndex>0</PrimaryNetworkConnectionIndex>\n  " \
              " <NetworkConnection\n      network=\"internal_network\">\n      " \
              "<NetworkConnectionIndex>0</NetworkConnectionIndex>\n     " \
              " <IpAddress>192.168.110.8</IpAddress>\n     " \
              " <IsConnected>false</IsConnected>\n   " \
              "   <IpAddressAllocationMode>MANUAL</IpAddressAllocationMode>\n" \
              "      <NetworkAdapterType>VMXNET3</NetworkAdapterType>\n" \
              "   </NetworkConnection>\n</NetworkConnectionSection>\n\n"
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Content-Type': "application/vnd.vmware.vcloud.networkConnectionSection+xml"
    }

    response = requests.request("PUT", url, verify=False, data=payload, headers=headers)

# Second
# ฟังก์ชันนี้จะทำงานเป็นฟังก์ชันที่ 2 ใช้สำหรับ Poweroff เครื่อง VM ที่ถอดขาแล้ว 7 วัน
# หลังจาก poweroff เครื่องแล้วจะทำการเปลี่ยนชื่อเครื่อง vm เป็น Vmname_Delete_11/07/62 เป็นในรูปแบบเดียวกัน คือเมื่อถอดขาครบ 7 วันแล้วจะบวก เวลาอีก 7 วันนำมาต่อท้ายชื่อ
def poweroff_vm_and_rename_vm(vcloud_token, vm_id, hostname):
    url = "https://"+hostname+"/api/vApp/"+vm_id+"/"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n" \
              "<Vm \n\txmlns=\"http://www.vmware.com/vcloud/v1.5\"\n" \
              "\txmlns:vmext=\"http://www.vmware.com/vcloud/extension/v1.5\" \n" \
              "\tneedsCustomization=\"true\" \n" \
              "\tnestedHypervisorEnabled=\"false\"\n" \
              "\tdeployed=\"false\" status=\"8\"\n" \
              "\tname=\"Wacc-280662_Delete_01/07/62\" \n" \
              "\ttype=\"application/vnd.vmware.vcloud.vm+xml\">\n" \
              "</Vm>\n"
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Content-Type': "application/vnd.vmware.vcloud.vm+xml"
    }

    response = requests.request("PUT", url, verify=False, data=payload, headers=headers)

    print(response.text)

# Third
# ฟังก์ชันนี้คือฟังก์ชันที่จะทำการ Delete Vm หลังจากที่ครบกำหนดระยะเวลาที่ poweroff เครื่องไว้จนครบวันที่กำหนดตามชื่อที่ได้ตั้งไว้
def Delete_vm(hostname, vcloud_token, vm_id):
    url = "https://"+hostname+"/api/vApp/"+vm_id+"/"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,

    }

    response = requests.request("DELETE", url, verify=False, data=payload, headers=headers)

    print(response.text)

# Fourth
# ฟังก์ชันนี้คือฟังก์ชันที่จะทำการ Poweroff Vapp  หลังเพื่อที่จะได้ Delete Vapp ได้ในฟังก์ชันถัดไป
def Poweroff_Vapp(hostname, vcloud_token,vapp_id):

    url = "https://"+hostname+"/api/vApp/"+vapp_id+"/action/undeploy"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<UndeployVAppParams\n" \
              " xmlns=\"http://www.vmware.com/vcloud/v1.5\">\n" \
              " <UndeployPowerAction>powerOff</UndeployPowerAction>\n" \
              "</UndeployVAppParams>"
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Content-Type': "application/vnd.vmware.vcloud.undeployVAppParams+xml"
    }

    response = requests.request("POST", url, verify=False, data=payload, headers=headers)

    print(response.text)

# Fifth
# ฟังก์ชันนี้จะทำงานหลังจาก poweroff vapp ไปแล้ว จะทำการลบ หรือ Delete Vapp
def Delete_vapp(hostname, vcloud_token,vapp_id):
    url = "https://"+hostname+"/api/vApp/"+vapp_id+"/"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Content-Type': "application/vnd.vmware.vcloud.undeployVAppParams+xml"
    }

    response = requests.request("DELETE", url, verify=False, data=payload, headers=headers)

    print(response.text)

# Sixth
# ฟังก์ชันนี้จะทำงานหลังจากที่ ทำการ Delete Vapp ไปแล้ว  โดยจะทำการ Delete Org Vdc Network ภายใต้ Edge Network ก่อนหรือว่า คือ วงที่เป็น ip Private นั้นเอง
def Delete_org_vdc_network(hostname, vcloud_token,org_vdc_network):
    url = "https://"+hostname+"/api/admin/network/"+org_vdc_network+"/"

    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Content-Type': "application/vnd.vmware.vcloud.task+xml"
    }

    response = requests.request("DELETE", url, verify=False, headers=headers)

    print(response.text)

# Seventh
# ฟังก์ชันนี้จะทำงานหลังจาก ลบ Org vdc network เสร็จแล้ว จะทำการลบ Edge Gateway หรือขาที่เป็น วง IP Public ที่เราเอาไว้ ออก Internet หรือว่า External Network นั้นเอง
def Delete_EdgeGateway(hostname, vcloud_token,Edgegateway_id):
    url = "https://"+hostname+"/api/admin/edgeGateway/"+Edgegateway_id+""

    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
    }

    response = requests.request("DELETE", url, verify=False, headers=headers)

    print(response.text)

# Eight
# ฟังก์ชันนี้จะทำงานหลังจากที่เราทำการลบ Edgegateway ออกไปแล้วเราจะทำการ disable VDC เพื่อที่จะทำการ Delete VDC ให้ได้ต้องทำการ disable VDC ก่อน
def Disable_Vdc(hostname, vcloud_token,vdc_id):
    url = "https://"+hostname+"/api/admin/vdc/"+vdc_id+"/action/disable"

    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token
    }

    response = requests.request("POST", url, verify=False, headers=headers)

    print(response.text)

# ninth
# ฟังก์ชันนี้จะทำงานหลังจากที่เราทำการ disable VDC เรียบร้อยแล้ว เราจะสามารถที่จะลบ VDC ได้ , Delete VDC
def Delete_Vdc(hostname, vcloud_token,vdc_id):
    url = "https://"+hostname+"/api/admin/vdc/"+vdc_id+"/"

    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token
    }

    response = requests.request("DELETE", url, verify=False, headers=headers)

    print(response.text)

# tenth
# ฟังก์ชันนี้จะทำงานหลังจากที่เราทำการ ลบ Vdc เรียบร้อยแล้วเราจะทำการ Disable Org เพื่อที่จะทำการ Delete ต่อไป
def Disable_org(hostname, vcloud_token,org_id):
    url = "https://"+hostname+"/api/admin/org/"+org_id+"/action/disable"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token
    }

    response = requests.request("POST", url, verify=False, data=payload, headers=headers)

    print(response.text)

# eleventh
# ฟังก์ชันนี้จะทำงานหลังจากที่เราทำการ ลบ Org หรือ Delete Org
def Delete_org(hostname, vcloud_token,org_id):
    url = "https://"+hostname+"/api/admin/org/"+org_id+"/"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token
    }

    response = requests.request("DELETE", url, verify=False, data=payload, headers=headers)

    print(response.text)

def enable_org(vcloud_token,org_id):

    url = "https://10.10.21.155/api/admin/org/"+org_id+"/action/enable"

    payload = ""
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Postman-Token': "d9612e04-507d-4a3d-8ad5-d6a81961a5e1"
    }

    response = requests.request("POST", url, verify=False, data=payload, headers=headers)
    # if response

    print(response.text)


def main():
    hostname = '10.10.21.155'
    username = "administrator@system"
    password = "6yHnmju&"
    org_id = "47ed0db8-8162-4908-b2b0-fc274be8bee9"
    vdc_id = ""
    vapp_id = ""
    vm_id = ""
    vm_name = "wacc_"
    Edgegateway_id = ""
    org_vdc_network = ""
    time = ""

    json_response(messages=None, status=None, headers=None)
    vcloud_token = create_sessions(hostname, username, password)
    ena_org = enable_org(vcloud_token,org_id)

    # dis_org = disable_org(vcloud_token,org_id)
    # rename = rename_vm(vcloud_token,vm_id, vm_name, time)
    # del_org = delete_org(vcloud_token,org_id)

main()