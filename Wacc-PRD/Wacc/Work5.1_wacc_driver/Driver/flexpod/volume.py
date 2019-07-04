import paramiko
import re
import cmd


hostname = '10.90.210.245'
username = 'sdi'
password = 'ZJ2~H59!!'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# "volume create -vserver INET_TEMP_SDI -volume ar_rai_kor_dai -size 20GB -aggregate aggr1_INET_Temp_02 -space-guarantee none -security-style unix -junction-path /ar_rai_kor_dai [-policy default]"
# volume create -vserver INET_TEMP_SDI -volume %s -size 1TB -aggregate aggr1_INET_Temp_02 -space-guarantee none' % volume_name

regex_aggregate_pattern = re.compile("aggr")
nix_aggregate_pattern = re.compile("aggr0")

regex_vserver_pattern = re.compile("INET_TEMP")


def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname="10.90.210.245",
        username="sdi",
        password="ZJ2~H59!!"
    )
    return client


def checkVserver():
    list_name = []
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname
    try:
        stdin, stdout, stderr = ssh.exec_command('vserver show-protocols')
        list_of_vserver = stdout.read()
        split_list_of_vserver = list_of_vserver.splitlines()
        # print split_list_of_vserver
        for line_count in range(0, len(split_list_of_vserver)-1):
            vserver_split = split_list_of_vserver[line_count].split()
            # print vserver_split
            vserver_filter = list(filter(regex_vserver_pattern.match, vserver_split))
            # print vserver_filter
            if not vserver_filter:
                pass
            else:
                dict_name = {
                    "vserverName": vserver_filter[0]
                }
                list_name.append(dict_name)
        # print list_name
            # list_name.append(vserver_split[0])
        #     list_name.append(vserver_filter)
        # print list_name
        # if vserver_name in list_name:
        #     print vserver_name, "debug"
        #     return "You can use this vserver, vserver name {}.".format(vserver_name), False
        # elif list_name == {}:
        #     return "You need to create vserver.", True
        # else:
        #     # return vserver, False
        # return "You don't have this vserver name.", True
        return list_name, True
    except Exception as e:
        return "You don't have this vserver name.", True
        # return e.message

def checkVolume():
    volume_list = []
    volume_dict = {}
    dict_name = {}
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname, True
    except:
        return "Failed to connect to % s" % hostname, True
    try:
        stdin, stdout, stderr = ssh.exec_command('volume show')
        list_of_volume = stdout.read()
        # print list_of_volume
        split_list_of_volume = list_of_volume.splitlines()
        # print split_list_of_volume
        for split_line_volume in range(2, len(split_list_of_volume)):
            split_volume_name = split_list_of_volume[split_line_volume].split()
            # print split_volume_name
            if not split_volume_name or split_volume_name[1] == "entries":
                pass
            else:
                # print split_volume_name
                vserver_name = split_volume_name[0]
                volume_name = split_volume_name[1]
                aggregate_name = split_volume_name[2]
                status_volume = split_volume_name[3]
                size_capacity = split_volume_name[5]
                available_capacity = split_volume_name[6]
                use_pct = split_volume_name[7]
                if vserver_name == "INET-Temp-01" or vserver_name == "INET-Temp-02":
                    pass
                else:
                    # print vserver_name, volume_name
                    volume_dict = {
                        "vServerName": vserver_name,
                        "volumeName": volume_name,
                        "aggregateName": aggregate_name,
                        "size": size_capacity,
                        "available": available_capacity,
                        "use": use_pct,
                        "status": status_volume
                    }
                    volume_list.append(volume_dict)
        # print volume_list

        # print name, "test"
        # print type(name), "test"
        # for line_count in range(0, len(split_list_of_volume) - 1):
        #     volume_split = split_list_of_volume[line_count].split()
        #     list_name.append(volume_split[1])
        #     # print list_name
        # print list_name, "ss"
        # if list_name == {}:
        #     # print "First name in volume."
        #     return None, False
        # if name not in list_name:
            # print "true\n"
            # return name, False
        return volume_list, True
    except Exception as e:
        # print "stop\n"
        return "Check volume fail", True
        # return e.message


def createVolume(vserver, volume_name, size, aggregate_name, unit_size):
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname
    try:
        # stdin, stdout, stderr = ssh.exec_command('volume create -vserver INET_TEMP_SDI -volume %s -size 1TB -aggregate aggr1_INET_Temp_02 -space-guarantee none' % volume_name)
        # stdin, stdout, stderr = ssh.exec_command('volume create -vserver INET_TEMP_SDI -volume test_junc_path '
        #                                          '-size 20GB -aggregate aggr1_INET_Temp_02 -space-guarantee none '
        #                                          '-security-style unix -junction-path /test_junc_path -policy default')
        stdin, stdout, stderr = ssh.exec_command('volume create -vserver {} -volume {} '
                                                 '-size {} -aggregate {} -space-guarantee none '
                                                 '-security-style unix -policy default'.format(
            vserver, volume_name, size, aggregate_name
        ))
        # print stdout.read()
        return_result = str(stdout.read()).split()
        error_result = return_result[1]
        if error_result == "Error:":
            result_dict = "Volume name {} has already in use".format(volume_name)
        else:
            result_dict = {
                "volumeName": volume_name,
                "size": size
            }
        return result_dict
    except Exception as e:
        # print e.message
        return "Create volume fail."


def getAggregate():
    result_list = []
    result_dict = {}
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname
    # try:
    stdin, stdout, stderr = ssh.exec_command('storage aggregate show')
    list_of_aggregate = stdout.read()
    split_list_of_aggregate = list_of_aggregate.splitlines()
    for line_count in range(0, len(split_list_of_aggregate)):
        aggregate_split = split_list_of_aggregate[line_count].split()
        aggregate_all_list = list(filter(regex_aggregate_pattern.match, aggregate_split))
        if not aggregate_all_list:
            pass
        else:
            nix_aggregate = list(filter(nix_aggregate_pattern.match, aggregate_split))
            if not nix_aggregate:
                # print aggregate_split
                aggregate_name = aggregate_split[0]
                aggregate_value = float(aggregate_split[3][0:2])
                result_dict = {
                    "aggregateName": aggregate_name,
                    "aggregateValue": str(100-aggregate_value)+" %"
                }
                result_list.append(result_dict)
    return result_list


def checkAggregate():
    list_name = []
    list_value = []
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname
    # try:
    stdin, stdout, stderr = ssh.exec_command('storage aggregate show')
    list_of_aggregate = stdout.read()
    split_list_of_aggregate = list_of_aggregate.splitlines()
    for line_count in range(0, len(split_list_of_aggregate)):
        aggregate_split = split_list_of_aggregate[line_count].split()
        aggregate_all_list = list(filter(regex_aggregate_pattern.match, aggregate_split))
        if not aggregate_all_list:
            pass
        else:
            nix_aggregate = list(filter(nix_aggregate_pattern.match, aggregate_split))
            if not nix_aggregate:
                # print aggregate_split
                aggregate_name = aggregate_split[0]
                aggregate_value = float(aggregate_split[3][0:2])
                list_name.append(aggregate_name)
                list_value.append(aggregate_value)
    min_value_index = list_value.index(min(list_value))
    aggregate_min_value = list_name[min_value_index]
    return aggregate_min_value
    # except Exception as e:
    #     return e.message


def offlineStatus(all_data):
    list_name = []
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    try:
        receive_data = all_data
        vserver_name = receive_data["vserverName"]
        volume_name = receive_data["volumeName"]
        zone = receive_data["zone"]
        real_volume_name = "{}_{}_{}".format(vserver_name, zone, volume_name)
        stdin, stdout, stderr = ssh.exec_command('volume ; offline -vserver %s -volume %s' %(vserver_name, real_volume_name))
        out_data = str(stdout.read())
        split_out = out_data.split()
        if split_out[0] == "Volume":
            return_result = "volume {}: {} is now offline".format(vserver_name, real_volume_name)
        else:
            return_result = "volume {}: {} is already offline".format(vserver_name, real_volume_name)
        return return_result, True
    except Exception as e:
        print "stop\n"
        return "offline volume false", False


def deleteVolume(all_data):
    volume_list = []
    volume_dict = {}
    dict_name = {}
    try:
        ssh = connect()
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname
    try:
        real_volume_name = ""
        stdin, stdout, stderr = ssh.exec_command('volume show')
        list_of_volume = stdout.read()
        # print list_of_volume
        split_list_of_volume = list_of_volume.splitlines()
        # print split_list_of_volume
        for split_line_volume in range(2, len(split_list_of_volume)):
            split_volume_name = split_list_of_volume[split_line_volume].split()
            if not split_volume_name or split_volume_name[1] == "entries":
                pass
            else:
                # print split_volume_name
                vserver_name = split_volume_name[0]
                volume_name = split_volume_name[1]
                status_volume = split_volume_name[3]

                if vserver_name == "INET-Temp-01" or vserver_name == "INET-Temp-02":
                    pass
                else:
                    # print vserver_name, volume_name
                    receive_data = all_data
                    send_vserver_name = receive_data["vserverName"]
                    send_volume_name = receive_data["volumeName"]
                    zone = receive_data["zone"]
                    real_volume_name = "{}_{}_{}".format(send_vserver_name, zone, send_volume_name)
                    if vserver_name == vserver_name and volume_name == real_volume_name and status_volume == "offline":
                        stdin, stdout, stderr = ssh.exec_command(
                            'volume ; delete -vserver %s -volume %s' %(vserver_name, volume_name))
                        return_value = str(stdout.read())
                        """
                        [Job 1025] Job succeeded: Successful
                        """
                        return "Delete volume {} success".format(real_volume_name)
                    elif vserver_name == vserver_name and volume_name == real_volume_name and status_volume == "online":
                        return "volume {} isn't offline".format(real_volume_name)
        return "Doesn't have volume {}".format(real_volume_name)
    except Exception as e:
        # print "stop\n"
        return "Delete volume fail"
        # return e.message


def mainBuildStorage(all_data):
    receive_data = all_data
    vserver_name = receive_data["vserverName"]
    volume_name = receive_data["volumeName"]
    zone = receive_data["zone"]
    size = receive_data["size"]
    unit_size = receive_data["unitSize"]
    if receive_data.has_key("aggregateName"):
        aggregate_name = receive_data["aggregateName"]
    else:
        aggregate_name = checkAggregate()
    real_volume_name = "{}_{}_{}".format(vserver_name, zone, volume_name)
    real_size = "{}{}".format(size, unit_size)
    build_volume = createVolume(vserver_name, real_volume_name, real_size, aggregate_name, unit_size)
    return build_volume


# def mainGetStorage():
#     # hostname = '10.90.210.245'
#     # username = 'sdi'
#     # password = 'ZJ2~H59!!'
#     zone = 'POC'
#     customer_name = 'obesity_01'
#     volume_name = zone + "_" + customer_name
#     aggregate_data = getAggregate()
#     return aggregate_data, "success"


# def mainVserver():
#     v, condition = checkVserver(hostname, username, password, vserver_name="INET_TEMP_SDI")
#     return v, condition



def buildStorage():
    a = "This is build storage"
    print a
    return a

