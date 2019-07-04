import paramiko
# import time
import re
# import cryptography


hostname = '10.20.200.20'
port = 22
username = 'sdivlan'
password = '7uJm,ki*'


equipped_pattern = re.compile(" ")
blade_pattern = re.compile("None")
# vlanid_pattern = re.compile("VLANID:")
org_all_list = []
dict_data_template = {}
# dict_data_name_vlan = {}
# dict_data_vlanid = {}
list_namevlan = []
list_vlanid = []


def session_ssh():
    try:
        ssh_vol = paramiko.SSHClient()
        ssh_vol.load_system_host_keys()
        ssh_vol.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_vol.connect(hostname, port, username, password)
        return ssh_vol
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname


def show_assoc():
    try:
        list_com_server_id = []
        shell_fi = session_ssh()
        com_list_in, com_list_out, com_list_err = shell_fi.exec_command("show server assoc ")
        com_assoc_detail = com_list_out.read().decode()
        # print vol_assoc_detail
        com_assoc_split = com_assoc_detail.splitlines()
        for com_data in range(2, len(com_assoc_split)):
            com_data_split = com_assoc_split[com_data].replace(" ", " ").split()
            com_server_id = com_data_split[0]
            list_com_server_id.append(com_server_id)
        # print list_com_server_id
            # blade_name = list(filter(blade_pattern.match, vol_data_split))
            #
            # if vol_data_split[1] == "None":
            #     pass
                # print(i1)

        com_list_in, com_list_out, com_list_err = shell_fi.exec_command("show server inventory detail")
        com_inventory_detail = com_list_out.read().decode()
        # print vol_detailx
        com_inventory_split = com_inventory_detail.splitlines()
        print com_inventory_detail
        for x in range(0, len(com_inventory_split)):
            print x
            # print com_inventory_split[x]
            # for x1 in x:
            x1 = x.split()
            # print(x1)
            # equipped_fil = list(filter(equipped_pattern.match, x1))
            # if x1 == "equipped_fil":
            # # print(x1)
            #     print(x1)
            if x1[4] != None and x1[4] == "Equipped":
                # print(x1)
                pass
            else:
                pass
        return "x"

    except Exception as e:
        print(e.message)
        return True


def list_name_org(shell_fi):
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
        print(list_org_name)

        # decode_name_org = "/"+create_org
        #     # return create_new_name_vlan, create_new_vlanid
        # for test in list_org_name:
        #     for test1 in test:
        #         if decode_name_org in test1:
        #             print('success')
        #             return create_org,False

        # return "Name Org is Wrong", True
    except Exception as e:
        print("false")
        return True


# def main():
#     hostname = '10.20.200.20'
#     port = 22
#     username = 'sdivlan'
#     password = '7uJm,ki*'
#
#     shell_fi = session_ssh(hostname, port, username, password)
#     # org_fi = list_name_org(shell_fi)
#     assoc = show_assoc(shell_fi)
#
# main()