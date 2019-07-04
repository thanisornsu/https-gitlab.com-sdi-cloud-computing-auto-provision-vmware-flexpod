# import xmljson
# import xmltodict, json
# import requests
#
# url = "https://10.10.21.155/api/sessions"
#
# payload = ""
# headers = {
#     'Accept': "application/*+xml;version=31.0",
#     'Authorization': "Basic YWRtaW5pc3RyYXRvckBzeXN0ZW06NnlIbm1qdSY=",
#     'User-Agent': "PostmanRuntime/7.11.0",
#     'Cache-Control': "no-cache",
#     'Postman-Token': "238638c7-f246-4a47-ab49-fca98affc6cb,ff997f9a-fc23-4b8e-9e3c-bd64c9b291b3",
#     # 'Host': "10.10.21.155",
#     # 'accept-encoding': "gzip, deflate",
#     # 'content-length': "",
#     # 'Connection': "keep-alive",
#     # 'cache-control': "no-cache"
#     }
#
# response = requests.request("POST", url, data=payload, headers=headers, verify=False)
#
# print(response.headers)

# org_data = {'Org_name': 'aao', 'username': 'administrator', 'vcloud_ip': '10.10.21.155', 'Org_url': 'https://10.10.21.155/cloud/org/aao/', 'Org_description': '1234', 'company_name': 'INET', 'org_key': '4c9b1562-12da-4dc4-a1c7-2c66fca9e28e', 'password': '6yHnmju&', 'customer_name': 'shanakan.ph'}
# user_data = {'password_vcloud': '6yHnmju&', 'username_vcloud': 'administrator', 'vcloud_ip': '10.10.21.155'}
# vcenter_data = {'template_name': 'Window Server 2012 r2', 'Disk': '40 GB', 'CPU': '1 Core', 'template_id': 'e05ab043-9f0f-47bb-85dc-d829df388c08', 'Memory': '4 GB'}
#
# dict_result = {}
#
# dict_result["username"] = user_data["username_vcloud"]
# dict_result["password"] = user_data["password_vcloud"]
# dict_result["vcloud_ip"] = user_data["vcloud_ip"]
# dict_result["org_name"] = org_data["Org_name"]
# dict_result["org_url"] = org_data["Org_url"]
# dict_result["org_description"] = org_data["Org_description"]
# dict_result["customer_name"] = org_data["customer_name"]
# dict_result["company_name"] = org_data["company_name"]
# dict_result["template_name"] = vcenter_data["template_name"]
# dict_result["cpu"] = vcenter_data["CPU"]
# dict_result["memory"] = vcenter_data["Memory"]
# dict_result["Disk"] = vcenter_data["Disk"]
#
# print dict_result

# jsonString = xmltodict.parse(response.text)
# print jsonString


# from flask import Flask, Response, json, request, abort, make_response, jsonify
# import requests
# import json
#
#
# url = "http://127.0.0.1:5000/test/post"
#
# payload = "{\n\t\"name\": \"AAA\",\n\t\"Age\": 12\n}"
# headers = {
#     'Content-Type': "application/json",
#     }
#
# response = requests.request("POST", url, data=payload, headers=headers)
#
# print(response.status_code)


# payload_data = {
#         "deployment_spec": {
#            "accept_all_EULA": True,
#            "name": "clientok5",
#            "default_datastore_id": "datastore-12",
#
#            "storage_provisioning": "thin",
#            "additional_parameters": [
#                {
#                    "@class": "com.vmware.vcenter.ovf.property_params",
#                    "properties": [
#                        {
#                            "instance_id": "",
#                            "class_id": "",
#                            "description": "The gateway IP for this virtual appliance.",
#                            "id": "gateway",
#                            "label": "Default Gateway Address",
#                            "category": "LAN",
#                            "type": "ip",
#                            "value": "10.1.2.1",
#                            "ui_optional": True
#                        }
#                    ],
#                    "type": "PropertyParams"
#                }
#            ]
#
#        },
#         "target": {
#             "folder_id": "group-v3",
#             "host_id": "host-9",
#             "resource_pool_id": "resgroup-21"
#         }
#     }
#
# a = json.dumps(payload_data)
#
# print type(a)


# disk_capacity = "3TB"
# disk_value = int(disk_capacity[0])
# disk_unit = disk_capacity[1:3]
#
# if disk_unit == "TB":
#     disk_real_value = disk_value*(1024**4)
# else:
#     disk_real_value = disk_value*(1024**3)
#
# print disk_real_value


# import xmljson
# import xmltodict, json
# import requests
#
# url = "https://10.10.21.155/api/org"
#
# payload = ""
# headers = {
#     'Accept': "application/*+xml;version=31.0",
#     'Authorization': "Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbmlzdHJhdG9yIiwiaXNzIjoiYTkzYzlkYjktNzQ3MS0zMTkyLThkMDktYThmN2VlZGE4NWY5QGQyZjRhYzJhLTU2ZGItNDNjMy04ZmYzLTQ3YzhiYzAwMjJkNCIsImV4cCI6MTU1NTc1MTY1MiwidmVyc2lvbiI6InZjbG91ZF8xLjAiLCJqdGkiOiIwY2UzOTIwZDYzNGY0MDViOWRiYmUyZjc4ZWNkMDJlMyJ9.dpBUorCT_FG7-229JxsCs6JcRX-9OnaBg1VrOmuJVBRS86vMhx0Zq7Ak69nc-F-MmspkvREa2e66YTwN5yv2KfkP6fT_o8tBEoAbb6qy0QvzuOI6pNFkQBClRe14GpJ6DefAGV2R9pej008b94yuawQ6fiqBCsllPg4Su-FWpiXuNEFp16mHpKhEhPJWRVL3aRDdyGgycLhhskqwOWAXtSGiHKh86YxXpOhfNrWIsc9CFBlxYZFYm8j02GjNwfBkFBhN5vK_k3cw8s0w4CPT9RSxEGG_OS3YKtO4vreKJKiIzimnrZ5Ho_3zlF9W1NjXSFtwvk1-fr8RhmwF-wJIcA",
#     'cache-control': "no-cache",
#     'Postman-Token': "69d178c3-6b32-4062-bba9-35e6dbc578f3"
#     }
#
# response = requests.request("GET", url, data=payload, headers=headers, verify=False)
#
# print(response.text)
#
# # print(response.text)
#
# jsonString = xmltodict.parse(response.text)
# print jsonString


dict_a = {
    "a": 1,
    "b": 2
}

dict_b = {
    "c": 3,
    "d": 4
}

dict_c = {
    "e": 5,
    "f": 6
}

dict_d = dict_a.copy()
dict_d.update(dict_b)
dict_d.update(dict_c)

print dict_d

