import requests
from flask import Flask, json, request, jsonify, session, abort, Response
# Import modules
import xml.etree.cElementTree as ET
from xmljson import badgerfish as bf
import json
import time
import urllib3
# import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import pymysql
import os
from sqlalchemy import create_engine
from yaml import load
import math
import paramiko
import base64
import xmltodict, json
import re

urllib3.disable_warnings()

data_vcloud = load(open("Driver\\flexpod\data_vcloud.yaml"))


def getVcenterVcloudDetail(cluster):
    vcloud_ip = data_vcloud["user"]["vcloud_ip"]
    username_vcloud = data_vcloud["user"]["username"]
    password_vcloud = data_vcloud["user"]["password"]
    dict_data = {"vcloud_ip": vcloud_ip,
                "vcloud_username": username_vcloud,
                "vcloud_password":password_vcloud}
    return dict_data


def create_sessions_network(cluster):
    print cluster["vcloud_ip"]
    print cluster["vcloud_username"]
    print cluster["vcloud_password"]
    hostname = cluster["vcloud_ip"]
    username = cluster["vcloud_username"]
    password = cluster["vcloud_password"]
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
            print y,"\nsessions"
            id_sess = response.headers.get("x-vcloud-authorization")
            print id_sess,"hhuhu"
            return id_sess
    except Exception as e:
        print e


def create_edge(vcloud_token, vdc, ip_external_start, ip_external_end, external_network,name):
    try:
        url = "https://10.10.21.155/api/admin/vdc/" + vdc + "/edgeGateways"

        payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<EdgeGateway\r\n   " \
                  "name=\""+name+"\"\r\n" \
                  "   xmlns=\"http://www.vmware.com/vcloud/v1.5\">\r\n   " \
                  "<Description>Example Edge Gateway</Description>\r\n   " \
                  "<Configuration>\r\n      <GatewayBackingConfig>compact</GatewayBackingConfig>\r\n      " \
                  "<GatewayInterfaces>\r\n         <GatewayInterface>\r\n            <Name>uplink1</Name>\r\n            " \
                  "<DisplayName>uplink1</DisplayName>\r\n            <Network\r\n               " \
                  "href=\"https://vcloud.example.com/api/admin/network/"+external_network+"\" />\r\n            " \
                  "<InterfaceType>uplink</InterfaceType>\r\n            <SubnetParticipation>\r\n               " \
                  "<Gateway>203.150.67.254</Gateway>\r\n               " \
                  "<Netmask>255.255.255.0</Netmask>\r\n               " \
                  "<IpRanges>\r\n                  <IpRange>\r\n                     " \
                  "<StartAddress>"+ip_external_start+"</StartAddress>\r\n                     " \
                  "<EndAddress>"+ip_external_end+"</EndAddress>\r\n                  " \
                  "</IpRange>\r\n               </IpRanges>\r\n            </SubnetParticipation>\r\n            " \
                  "<UseForDefaultRoute>true</UseForDefaultRoute>\r\n         </GatewayInterface>\r\n      " \
                  "</GatewayInterfaces>\r\n      <HaEnabled>false</HaEnabled>\r\n      " \
                  "<UseDefaultRouteForDnsRelay>false</UseDefaultRouteForDnsRelay>\r\n   " \
                  "</Configuration>\r\n</EdgeGateway>"
        headers = {
            'Content-Type': "application/vnd.vmware.admin.edgeGateway+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
        }

        response = requests.request("POST", url, verify=False, data=payload, headers=headers)
        print "create_edge response:",response.status_code, response.text
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        y = json.loads(jsonStr)
        print y, "\nvdc_id"
        task_url = y['EdgeGateway']['Tasks']['Task']['@href']
        edge_gateway_url = y['EdgeGateway']['Tasks']['Task']['Owner']['@href']
        # start_time = time.time()
        # while True:
        #     if start_time-time.time()> 300:
        #         return "",False
        #     response_task = requests.request("GET", task_url, verify=False, headers=headers)
        #     print response_task.status_code, '>>>>', response_task.text
        #     if response_task.text.__contains__("status=\"success\""):
        #         break
        #     doc = ET.fromstring(response.text.encode('utf-8'))
        #     jsonStr = json.dumps(bf.data(doc))
        #     jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        #     y = json.loads(jsonStr)
        #     print 'V='*25,'json','=V'*25
        #     print 'edge gate way data', y
        #     print '-'*50
        #     time.sleep(5)
        # while True:
        #     response_task  = requests.request("GET", task_url, verify=False, headers=headers)
        #     print response_task.status_code,'>>>>',response_task.text
        #     doc = ET.fromstring(response.text.encode('utf-8'))
        #     jsonStr = json.dumps(bf.data(doc))
        #     jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        #     y = json.loads(jsonStr)
            # print y, "\nvdc_id"
            # print '%s%s'%('-'*50,y)
            # time.sleep(1)


        if response.status_code == 201:
            return [task_url,edge_gateway_url],False
        else:
            return "false", True
    except Exception:
        return {"message": "Create edge error"}, True


def external_network_id(vcloud_token):
    try:
        url = "https://10.10.21.155/api/admin/extension/externalNetworkReferences"

        headers = {
            'Content-Type': "application/vnd.vmware.vcloud.orgVdcNetwork+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
        }
        response = requests.request("GET", url, verify=False, headers=headers)
        # print(response.text)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/extension/v1.5}", "")
        y = json.loads(jsonStr)
        external_network = y["VMWExternalNetworkReferences"]["ExternalNetworkReference"]["@id"]
        external_network = external_network.split(":")
        print external_network[3], "External network"
        return external_network[3], False
    except Exception as e:
        return "false",True


def edgeGateways(vcloud_token,vdc_id):
    try:
        url = "https://10.10.21.155/api/admin/vdc/"+vdc_id+"/edgeGateways"

        headers = {
            'Content-Type': "application/vnd.vmware.vcloud.orgVdcNetwork+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
        }

        response = requests.request("GET", url,verify = False, headers=headers)
        print '%s\n %s %s'%('-'*20, 'get edge gateway', response.text)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        y = json.loads(jsonStr)
        # print y, "\nvdc_id"
        print y["QueryResultRecords"]["EdgeGatewayRecord"]["@href"],"\ntest"
        gateway  = y["QueryResultRecords"]["EdgeGatewayRecord"]["@href"]
        gateway =  gateway.split("/")
        # print gateway[6]
        return gateway[6],False
    except Exception as e:
        return "false",True


def org_vdc_network_id(vcloud_token):
    url = "https://10.10.21.155/api/admin/vdc/82f1f86a-a56a-4bc6-a73f-4bda0b2792e7/networks"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<OrgVdcNetwork\r\n   name=\"ORMOVDCNet\"\r\n   " \
              "xmlns=\"http://www.vmware.com/vcloud/v1.5\">\r\n   <Description>Routed through an Edge Gateway</Description>\r\n   " \
              "<Configuration>\r\n      <IpScopes>\r\n         <IpScope>\r\n            <IsInherited>false</IsInherited>\r\n            " \
              "<Gateway>192.168.10.254</Gateway>\r\n            " \
              "<Netmask>255.255.255.0</Netmask>\r\n            " \
              "<Dns1>203.150.213.1</Dns1>\r\n            <Dns2>203.150.218.161</Dns2>\r\n            " \
              "<DnsSuffix>example.com</DnsSuffix>\r\n            <IpRanges>\r\n               " \
              "<IpRange>\r\n                  <StartAddress>192.168.10.1</StartAddress>\r\n                  " \
              "<EndAddress>192.168.10.253</EndAddress>\r\n               </IpRange>\r\n            </IpRanges>\r\n         " \
              "</IpScope>\r\n      </IpScopes>\r\n      <FenceMode>natRouted</FenceMode>\r\n   </Configuration>\r\n   " \
              "<EdgeGateway\r\n      " \
              "href=\"https://10.10.21.155/api/admin/gateway/09ae6ffe-ecbf-4830-920c-545aa2ba81b7\" />\r\n  " \
              " <IsShared>false</IsShared>\r\n</OrgVdcNetwork>"
    headers = {
        'Content-Type': "application/vnd.vmware.vcloud.orgVdcNetwork+xml",
        'x-vcloud-authorization': vcloud_token,
        'Accept': "application/*+xml;version=31.0",
    }

    response = requests.request("GET", url,verify = False, data=payload, headers=headers)
    # print(response.text)
    doc = ET.fromstring(response.text.encode('utf-8'))
    jsonStr = json.dumps(bf.data(doc))
    jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
    y = json.loads(jsonStr)
    print y,"\ntest"
    print y["QueryResultRecords"]["OrgVdcNetworkRecord"]["@href"]
    network_id = y["QueryResultRecords"]["OrgVdcNetworkRecord"]["@href"]
    print network_id.split("/")
    network_id = network_id.split("/")
    print network_id[6],"last"
    return network_id[6],False



def org_vdc_network(vcloud_token, vdc, ip_internal_start, ip_internal_end,gateway_id,name):
    # try:
    url = "https://10.10.21.155/api/admin/vdc/"+vdc+"/networks"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<OrgVdcNetwork\r\n   " \
              "name=\""+name+"\"\r\n   xmlns=\"http://www.vmware.com/vcloud/v1.5\">\r\n   " \
              "<Description>Routed through an Edge Gateway</Description>\r\n   <Configuration>\r\n      " \
              "<IpScopes>\r\n         <IpScope>\r\n            <IsInherited>false</IsInherited>\r\n            " \
              "<Gateway>192.168.10.254</Gateway>\r\n            <Netmask>255.255.255.0</Netmask>\r\n            " \
              "<Dns1>203.150.213.1</Dns1>\r\n            <Dns2>203.150.218.161</Dns2>\r\n            " \
              "<DnsSuffix>example.com</DnsSuffix>\r\n            <IpRanges>\r\n               <IpRange>\r\n                  " \
              "<StartAddress>"+ip_internal_start+"</StartAddress>\r\n                  " \
              "<EndAddress>"+ip_internal_end+"</EndAddress>\r\n               " \
              "</IpRange>\r\n            </IpRanges>\r\n         </IpScope>\r\n      </IpScopes>\r\n      " \
              "<FenceMode>natRouted</FenceMode>\r\n   </Configuration>\r\n   <EdgeGateway\r\n      " \
              "href=\"https://10.10.21.155/api/admin/gateway/"+gateway_id+"\" />\r\n   " \
              "<IsShared>false</IsShared>\r\n</OrgVdcNetwork>"
    headers = {
        'Content-Type': "application/vnd.vmware.vcloud.orgVdcNetwork+xml",
        'x-vcloud-authorization': vcloud_token,
        'Accept': "application/*+xml;version=31.0",
    }

    response = requests.request("POST", url,verify = False, data=payload, headers=headers)
    print ">>>>>>org network:",response.status_code,response.text
    doc = ET.fromstring(response.text.encode('utf-8'))
    jsonStr = json.dumps(bf.data(doc))
    jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
    y = json.loads(jsonStr)
    task_url = y['OrgVdcNetwork']['Tasks']['Task']['@href']
    org_vdc_network_url = y['OrgVdcNetwork']['Tasks']['Task']['Owner']['@href']
    print task_url,"task_url"
    print org_vdc_network_url,"org_vdc_network_url"
    return [task_url,org_vdc_network_url],False
    # except Exception as e:
    #     return "false", True


def modify_nat(vcloud_token,edgeGateway_id,ip_external_end, ip_internal_start,id_network):

    url = "https://10.10.21.155/api/admin/edgeGateway/"+edgeGateway_id+"/action/configureServices"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<EdgeGatewayServiceConfiguration\r\n   " \
              "xmlns=\"http://www.vmware.com/vcloud/v1.5\">\r\n <NatService>\r\n <IsEnabled>true</IsEnabled>\r\n  " \
              "<NatRule>\r\n  " \
              "<RuleType>DNAT</RuleType>\r\n    " \
              "<IsEnabled>true</IsEnabled>\r\n    <GatewayNatRule>\r\n       " \
              "<Interface\r\n          " \
              "href=\"https://10.10.21.155/api/admin/network/7cf14a6f-1d5c-4b06-ae1a-e87959191166\" />\r\n       " \
              "<OriginalIp>"+ip_external_end+"</OriginalIp>\r\n       " \
              "<OriginalPort>any</OriginalPort>\r\n       " \
              "<TranslatedIp>"+ip_internal_start+"</TranslatedIp>\r\n       " \
              "<TranslatedPort>any</TranslatedPort>\r\n       " \
              "<Protocol>any</Protocol>\r\n    </GatewayNatRule>\r\n  </NatRule>\r\n  <NatRule>\r\n  <RuleType>DNAT</RuleType>\r\n    " \
              "<IsEnabled>true</IsEnabled>\r\n    <GatewayNatRule>\r\n       <Interface\r\n          " \
              "href=\"https://10.10.21.155/api/admin/network/"+id_network+"\" />\r\n       " \
              "<OriginalIp>"+ip_external_end+"</OriginalIp>\r\n       <OriginalPort>any</OriginalPort>\r\n       " \
              "<TranslatedIp>"+ip_internal_start+"</TranslatedIp>\r\n       <TranslatedPort>any</TranslatedPort>\r\n       " \
              "<Protocol>any</Protocol>\r\n    " \
              "</GatewayNatRule>\r\n  </NatRule>\r\n  <NatRule>\r\n    " \
              "<RuleType>SNAT</RuleType>\r\n    <IsEnabled>true</IsEnabled>\r\n    " \
              "<GatewayNatRule>\r\n       " \
              "<Interface\r\n          " \
              "href=\"https://10.10.21.155/api/admin/network/"+id_network+"\" />\r\n       " \
              "<OriginalIp>"+ip_internal_start+"</OriginalIp>\r\n       " \
              "<TranslatedIp>"+ip_external_end+"</TranslatedIp>\r\n       " \
              "<Protocol>any</Protocol>\r\n    </GatewayNatRule>\r\n  </NatRule>\r\n  <NatRule>\r\n    " \
              "<RuleType>SNAT</RuleType>\r\n    " \
              "<IsEnabled>true</IsEnabled>\r\n    <GatewayNatRule>\r\n       <Interface\r\n          " \
              "href=\"https://10.10.21.155/api/admin/network/7cf14a6f-1d5c-4b06-ae1a-e87959191166\" />\r\n       " \
              "<OriginalIp>"+ip_internal_start+"</OriginalIp>\r\n       " \
              "<TranslatedIp>"+ip_external_end+"</TranslatedIp>\r\n       " \
              "<Protocol>any</Protocol>\r\n    " \
              "</GatewayNatRule>\r\n  </NatRule>" \
              "</NatService>\r\n" \
              "</EdgeGatewayServiceConfiguration>"
    headers = {
        'Content-Type': "application/vnd.vmware.admin.edgeGatewayServiceConfiguration+xml",
        'x-vcloud-authorization': vcloud_token,
        'Accept': "application/*+xml;version=31.0",
    }

    response = requests.request("POST", url, verify = False,data=payload, headers=headers)
    print('modify nat>>>>>',response.text)
    return "test",False


def add_network_vapp(vcloud_token,vapp_id, name_org_vdc_network,ip_gateway,netmask,start_ip_address,end_ip_address,id_network):
    url = "https://10.10.21.155/api/vApp/"+vapp_id+"/networkConfigSection"

    payload = "<NetworkConfigSection\n   xmlns=\"http://www.vmware.com/vcloud/v1.5\"\n " \
              "xmlns:ovf=\"http://schemas.dmtf.org/ovf/envelope/1\">\n " \
              "<ovf:Info>Configuration parameters for logical networks</ovf:Info>\n    " \
              "<NetworkConfig networkName=\""+name_org_vdc_network+"\">\n      " \
              "<Description></Description>\n        <Configuration>\n         " \
              "<IpScopes>\n                " \
              "<IpScope>\n                 " \
              "<IsInherited>true</IsInherited>\n                    " \
              "<Gateway>"+ip_gateway+"</Gateway>\n  " \
              "<Netmask>"+netmask+"</Netmask>\n          " \
              "<SubnetPrefixLength>24</SubnetPrefixLength>\n                 " \
              "<Dns1>203.150.213.1</Dns1>\n                   " \
              "<Dns2>203.150.218.161</Dns2>" \
              "<IsEnabled>true</IsEnabled>" \
              "<IpRanges>\n" \
              "<IpRange>\n" \
              "<StartAddress>"+start_ip_address+"</StartAddress>\n" \
              "<EndAddress>"+end_ip_address+"</EndAddress>\n" \
              "</IpRange>\n                    </IpRanges>\n" \
              "</IpScope>\n            </IpScopes>\n            <ParentNetwork \n" \
              "\ttype=\"application/vnd.vmware.vcloud.network+xml\"\n            " \
              "\tname=\""+name_org_vdc_network+"\"\n" \
              "\thref=\"https://10.10.21.155/api/admin/network/"+id_network+"\" />\n" \
              "<FenceMode>bridged</FenceMode>\n            " \
              "<RetainNetInfoAcrossDeployments>false</RetainNetInfoAcrossDeployments>\n" \
              "<GuestVlanAllowed>false</GuestVlanAllowed>\n        </Configuration>\n        " \
              "<IsDeployed>false</IsDeployed>\n    " \
              "</NetworkConfig>\n</NetworkConfigSection>"
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token ,
        'Content-Type': "application/vnd.vmware.vcloud.networkConfigSection+xml",

        }

    response = requests.request("PUT", url, verify=False, data=payload, headers=headers)
    # try:
        # print response.status_code, "test"
        # if response.status_code == 202:
        #     return "A", False
        # else:
        #     return "false", True
    doc = ET.fromstring(response.text.encode('utf-8'))
    jsonStr = json.dumps(bf.data(doc))
    jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
    y = json.loads(jsonStr)
    print y,"test"
    task_url = y['Task']['@href']
    # network_url = y['NetworkConfig']['Tasks']['Task']['Owner']['@href']
    print task_url, "task_url"
    # task_url = "http://"+task_url
    print task_url, "task_url"
    # print network_url, "org_vdc_network_url"
    return task_url, False
    # except Exception as e:
    #     print "false"
    #     return "false", True


def vapp_id(vcloud_token,vdc_id):

    try:
        url = "https://10.10.21.155/api/vdc/"+vdc_id+""

        headers = {
            'Content-Type': "application/vnd.vmware.admin.organization+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
        }

        response = requests.request("GET", url,verify = False, headers=headers)
        # print(response.text)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        y = json.loads(jsonStr)
        # print y, "\ntest"
        print y["Vdc"]["ResourceEntities"]["ResourceEntity"]["@href"],"debug"
        vapp_id = y["Vdc"]["ResourceEntities"]["ResourceEntity"]["@href"].split("/")
        print vapp_id[5]
        return vapp_id[5],False
    except Exception as e:
        print "false"
        return "false", True



#
# def vmID(vcloud_token,vapp):
#
#     try:
#         url = "https://10.10.21.155/api/vApp/"+vapp
#
#         headers = {
#             'Content-Type': "application/vnd.vmware.admin.organization+xml",
#             'x-vcloud-authorization': vcloud_token,
#             'Accept': "application/*+xml;version=31.0",
#         }
#
#         response = requests.request("GET", url,verify = False, headers=headers)
#         # print(response.text)
#         doc = ET.fromstring(response.text.encode('utf-8'))
#         jsonStr = json.dumps(bf.data(doc))
#         jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
#         y = json.loads(jsonStr)
#         print y
#         print y
#         # print y
#         # print y["VApp"],"ddd"
#         # print y["VApp"]["@href"]
#         # for i in y["VApp"]:
#         #     print i
#         # print y["VApp"]["Children"]
#         # print y["VApp"]["Children"]["Vm"]["@name"]
#         # print y["VApp"]["Children"]["Vm"]["@href"]
#         # vm_id = y["VApp"]["@href"]
#         # vm_id = vm_id.split("/")
#         # print vm_id[5]
#         # return vm_id[5], False
#     except Exception as e:
#         print "false"
#         return "false", True


def vmID(vcloud_token,vapp):
    try:
        url = "https://10.10.21.155/api/vApp/"+vapp

        headers = {
            'Content-Type': "application/vnd.vmware.admin.organization+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
        }

        response = requests.request("GET", url,verify = False, headers=headers)
        # print(response.text)
        doc = ET.fromstring(response.text.encode('utf-8'))
        jsonStr = json.dumps(bf.data(doc))
        jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
        y = json.loads(jsonStr)
        print y
        print y["VApp"]["Children"]["Vm"]["@name"]
        print y["VApp"]["Children"]["Vm"]["@href"]
        vm_id = y["VApp"]["Children"]["Vm"]["@href"]
        vm_id = vm_id.split("/")
        print vm_id[5]
        return vm_id[5], False
    except Exception as e:
        print "false"
        return "false", True


def vm_connect_network(vcloud_token, vm_id, name_org_vdc_network, start_ip_address):
    url = "https://10.10.21.155/api/vApp/" + vm_id + "/networkConnectionSection/"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<NetworkConnectionSection \n" \
              "   type=\"application/vnd.vmware.vcloud.networkConnectionSection+xml\"\n" \
              "   xmlns=\"http://www.vmware.com/vcloud/v1.5\"\n   xmlns:ovf=\"http://schemas.dmtf.org/ovf/envelope/1\">\n" \
              "   <ovf:Info>Firewall allows access to this address.</ovf:Info>\n" \
              "   <PrimaryNetworkConnectionIndex>0</PrimaryNetworkConnectionIndex>\n" \
              "   <NetworkConnection\n      network=\"" + name_org_vdc_network + "\">\n      <NetworkConnectionIndex>0</NetworkConnectionIndex>\n" \
              "      <IpAddress>" + start_ip_address + "</IpAddress>\n      \n      <IsConnected>true</IsConnected>\n" \
              "      <IpAddressAllocationMode>MANUAL</IpAddressAllocationMode>\n   </NetworkConnection>\n</NetworkConnectionSection>"
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'x-vcloud-authorization': vcloud_token,
        'Content-Type': "application/vnd.vmware.vcloud.networkConnectionSection+xml",

    }

    response = requests.request("PUT", url, verify=False, data=payload, headers=headers)

    doc = ET.fromstring(response.text.encode('utf-8'))
    jsonStr = json.dumps(bf.data(doc))
    jsonStr = jsonStr.replace("{http://www.vmware.com/vcloud/v1.5}", "")
    y = json.loads(jsonStr)
    print y,"test"
    print y["Task"]["@href"],"ddddtest"
    id = y["Task"]["@href"]
    # id = id.split("/")[-1]
    # print y["VApp"]["Children"]["Vm"]["@href"]
    # vm_id = y["VApp"]["Children"]["Vm"]["@href"]
    # vm_id = vm_id.split("/")
    # print vm_id[5]
    # return vm_id[5], False
    return id,False


def session_ssh(hostname,port,  username , password):

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print "Connected to %s" % hostname
        return ssh
    except paramiko.AuthenticationException:
        print "Failed to connect to % s due to wrong username / password" % hostname
        exit(1)
    except:
        print "Failed to connect to % s" % hostname
        exit(2)


def command(shell_fi, create_new_name_vlan, create_new_vlanid):
    # shell_fi = session_ssh()
    list_vlanid = []
    list_namevlan = []
    vlanid_pattern = re.compile("VLANID:")
    namevlan_pattern = re.compile("Name:")
    try:

        vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command("scope eth-uplink ; show vlan expand")
        vol_detail = vol_list_out.read().decode()
        vol_detail1 = vol_detail.split("\n")
        for i in vol_detail1:
            i1 = i.replace(" ", "").split("\n")

            namevlan_all_list = list(filter(namevlan_pattern.match, i1))
            vlanid_all_list = list(filter(vlanid_pattern.match, i1))

            if namevlan_all_list:
                namevlan_all_list1 = namevlan_all_list[0].split(":")
                list_namevlan.append(namevlan_all_list1[1])
            else:

                if vlanid_all_list:
                    vlanid_all_list1 = vlanid_all_list[0].split(":")
                    list_vlanid.append(vlanid_all_list1[1])


        if create_new_name_vlan in list_namevlan and create_new_vlanid in list_vlanid:
            print('success')

            return create_new_name_vlan, True

        return "Create Vlan", "create"
    except Exception as e:
        return "Create Vlan", True


def create_vlan(shell_fi,create_new_name_vlan ,create_new_vlanid):

    vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command(
        "scope eth-uplink ; create vlan "+create_new_name_vlan+" "+create_new_vlanid+" ; create member-port-channel a 100 ; exit ; create member-port-channel b 200 ; exit; commit-buffer")
    # vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command("scope eth-uplink ; create vlan {}_{} {} ; create member-port-channel a 100 ; exit ; create member-port-channel b 200 ; exit; commit-buffer".format(create_new_name_vlan, create_new_vlanid, create_new_vlanid))
    vol_detail = vol_list_out.read().decode()
    vol_detail1 = vol_detail.split("\n")

    print(vol_detail1)


def list_name_org(shell_fi, create_org):
    list_org_name = []
    org_pattern = re.compile("/")
    try:
        vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command("show org")
        vol_detail = vol_list_out.read().decode()
        vol_detail1 = vol_detail.splitlines()

        for i in vol_detail1:
            i1 = i.replace(" ", "").split("\n")
            org_name = list(filter(org_pattern.match, i1))

            if org_name:
                org_name1 = org_name[0].splitlines()
                list_org_name.append(org_name1)
            else:
                pass

        decode_name_org = "/"+create_org
        #     # return create_new_name_vlan, create_new_vlanid
        for test in list_org_name:
            for test1 in test:
                if decode_name_org in test1:
                    print('success')
                    return create_org,False

        return "Name Org is Wrong",True
    except Exception as e:
        print "false"
        return None, True


def check_task_status(task_url,vcloud_token):
    start_time = time.time()
    while True:
        if start_time - time.time() > 300:
            return False
            print "over time"
        headers = {
            'Content-Type': "application/vnd.vmware.admin.edgeGateway+xml",
            'x-vcloud-authorization': vcloud_token,
            'Accept': "application/*+xml;version=31.0",
        }
        try:
            response_task = requests.request("GET", task_url, verify=False, headers=headers)
            # print response_task.status_code, '>>>>', response_task.text
            if response_task.text.__contains__("status=\"success\""):
                return True
        except Exception as ex:
            print "error get task:", ex.message
            return False
        time.sleep(5)


def org(shell_fi, create_org, create_new_name_vlan,interface_one,interface_two):
    # shell_fi = session_ssh()
    list_org = []
    org_all_list = []
    dict_data_template = {}
    org_eth_pattern = re.compile(create_org)
    # print(create_org)
    try:
        vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command("scope org "+create_org+" ; sh vnic-templ")
        vol_detail = vol_list_out.read().decode()
        vol_detail1 = vol_detail.splitlines()

        for org_tem in vol_detail1:
            org_tem1 = org_tem.split("/")
            org_all_list = list(filter(org_eth_pattern.match, org_tem1))
            if org_all_list:
                org_tem2 = org_all_list[0].split(" ")

                print(org_tem2[0]),"seww"
                list_org.append(org_tem2[0])
        if interface_one in list_org:
            print "You can use"+interface_one
        else:
            dict = {"message" : "You can't use this interface : "+interface_one}
            return json.dumps(dict)
        if interface_two in list_org:
            print "You can use"+interface_two
        else:
            dict = {"message" : "You can't use this interface : "+interface_two}
            return json.dumps(dict)


        vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command("scope org " + create_org + " ; scope vnic-templ "+interface_one+" \
        ; create eth-if "+create_new_name_vlan+" ; commit-buffer")

        vol_list_in, vol_list_out, vol_list_err = shell_fi.exec_command("scope org " + create_org + " ; scope vnic-templ " + interface_two + " \
        ; create eth-if " + create_new_name_vlan + " ; commit-buffer")
        vol_detail = vol_list_out.read().decode()

        # print('success' , org_tem2[0])
        # print(create_new_name_vlan)
        print list_org[0],"aa"
        return "test",False

    except Exception as e:
        print(e.message)
        return None, True


def guestCustomization(vcloud_token,vmm,computer_name):

    url = "https://10.10.21.155/api/vApp/"+vmm+"/guestCustomizationSection/"

    payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<GuestCustomizationSection\n   " \
              "xmlns=\"http://www.vmware.com/vcloud/v1.5\"\n " \
              "  xmlns:ovf=\"http://schemas.dmtf.org/ovf/envelope/1\"\n   " \
              "ovf:required=\"false\">\n   <ovf:Info>Specifies Guest OS Customization Settings</ovf:Info>\n   " \
              "<Enabled>true</Enabled>\n   <ChangeSid>false</ChangeSid>\n   " \
              "<ComputerName>"+computer_name+"</ComputerName>\n</GuestCustomizationSection>"
    headers = {
        'Accept': "application/*+xml;version=31.0",
        'Authorization': "Basic YWRtaW5pc3RyYXRvckB2c3BoZXJlLmxvY2FsOkFkbWluITIz",
        'x-vcloud-authorization': vcloud_token,
        }

    response = requests.request("PUT", url, verify = False, data=payload, headers=headers)

    print(response.text)
    return "s", False


def all_network(vcloud_data, frontend_data):
# try:
    # header = request.headers
    header = {"BD": "flexpod"}
    # data = request.json
    ip_gateway = "192.168.0.254"
    netmask = "255.255.255.0"
    # data = {"customer_name" : "lup_wacc_Cust",
    #         "vdc_id" : "eca56070-bd60-4f96-85c1-cb2c9778be02",
    #         "ip_internal_start" : "192.168.10.1",
    #         "ip_internal_end" : "192.168.10.253",
    #         "ip_external_start": "203.150.67.112",
    #         "ip_external_end": "203.150.67.113"
    #         }
    vdc_id = vcloud_data["vdcId"]
    customer_name = frontend_data["customerName"]
    # ip_internal_start = frontend_data["ipInternalStart"]
    # ip_internal_end = frontend_data["ipInternalEnd"]
    # ip_external_start = frontend_data["ipExternalStart"]
    # ip_external_end = frontend_data["ipExternalEnd"]
    ip_internal_start = "192.168.10.1"
    ip_internal_end = "192.168.10.253"
    ip_external_start = "203.150.67.112"
    ip_external_end = "203.150.67.113"
    cluster = getVcenterVcloudDetail("test")
    vcloud_token = create_sessions_network(cluster)
    # print vcloud_token, "debug"
    external_network, err = external_network_id(vcloud_token)
    if not err:
        gateway_data, err = create_edge(vcloud_token, vdc_id, ip_external_start, ip_external_end, external_network, customer_name)
        #--------------
        print "gate ERROR???????????????????????"
        if not err:
            task_edge_url = gateway_data[0]
            gateway_url = gateway_data[1]
            gateway_id = gateway_url.split('/')[-1]
            task_edge_status = check_task_status(task_edge_url,vcloud_token)

            print "create edge success"
            if task_edge_status:
                org,err = org_vdc_network(vcloud_token, vdc_id, ip_internal_start, ip_internal_end, gateway_id, customer_name)
                if not err:
                    # print org,"data org"
                    print org[0],"test1"
                    print org[1],"test2"
                    # return "D"
                    task_ovn_url,ovn_id = org[0], org[1].split('/')[-1]
                    task_ovn_status = check_task_status(task_ovn_url, vcloud_token)
                    print task_ovn_status,"task ovn url"
                    # print ovn_id,"ovn id"
                    # return "ffL"
                    if task_ovn_status:
                        print "create org vdc success"
                        nat,err = modify_nat(vcloud_token, gateway_id, ip_external_end, ip_internal_start, ovn_id)
                        if not err:
                            print "create nat success"
                            # return "GG"
                            vapp, err = vapp_id(vcloud_token, vdc_id)
                            if not err:
                                network_vapp,err = add_network_vapp(vcloud_token, vapp, customer_name, ip_gateway, netmask, ip_internal_start, ip_internal_end, ovn_id)
                                if not err:
                                    print "network vapp success"
                                    # task_anv_url = network_vapp.split('/')[-1]
                                    # print task_anv_url,"test task_anv_url"
                                    # task_anv_url = "https://"+task_anv_url
                                    task_anv_status = check_task_status(network_vapp, vcloud_token)
                                    print "check task success"
                                    # return "Savee overload"
                                    vm_id, err = vmID(vcloud_token, vapp)
                                    if not err:
                                        print vm_id, "test id vm"
                                        vm,err = vm_connect_network(vcloud_token, vm_id, customer_name, ip_internal_start)
                                        if not err:
                                            print "create vm_connect_network success"
                                            guest, err = guestCustomization(vcloud_token, vm_id, customer_name)
                                            if not err:
                                                print "Enable Guest"
                                                return_data = {"message": "Create NSX success"}
                                                # dict = {"header": header,
                                                #         "customer_name": data["customer_name"],
                                                #         "ip_internal_start": data["ip_internal_start"],
                                                #         "ip_external_end": data["ip_external_end"],
                                                #         "message": "You connect network vapp success already."}
                                                # return json.dumps(dict)
                                                return True, return_data
                                            else:
                                                dict = {"message": "You can not enable guest customize."}
                                                return False, dict
                                        else:
                                            dict = {"message": "You can not connect network vm."}
                                            return False, dict
                                    else:
                                        dict = {"message": "You can not get vm_id."}
                                        return False, dict
                                else:
                                    dict = {"message": "You can not connect network vapp."}
                                return False, dict
                            else:
                                dict = {"message": "You can not connect vapp_id."}
                            return False, dict
                        else:
                            dict = {"message": "You can not connect Nat."}
                            return False, dict
                    else:
                        dict = {"message": "You can not connect org_vdc_network_id."}
                    return False, dict
                else:
                    dict = {"message": "You can not connect org_vdc_network."}
                return False, dict
            else:
                dict = {"message": "You can not get gateway id."}
                return False, dict
        else:
            dict = {"message": "You can not create edge."}
            return False, dict
    else:
        dict = {"message": "You can not get external network."}
        # return json.dumps(dict)
        return False, dict

    # except Exception as e:
    #     print e
    #     dict = {"message": "Error creating network."}
    #     return json.dumps(dict)
    #
