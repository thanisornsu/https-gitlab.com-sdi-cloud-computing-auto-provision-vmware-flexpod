import paramiko
import re
import cmd


hostname = '10.90.210.245'
username = 'sdi'
password = 'ZJ2~H59!!'


# "volume create -vserver INET_TEMP_SDI -volume ar_rai_kor_dai -size 20GB -aggregate aggr1_INET_Temp_02 -space-guarantee none -security-style unix -junction-path /ar_rai_kor_dai [-policy default]"
# volume create -vserver INET_TEMP_SDI -volume %s -size 1TB -aggregate aggr1_INET_Temp_02 -space-guarantee none' % volume_name

regex_aggregate_pattern = re.compile("aggr")
nix_aggregate_pattern = re.compile("aggr0")

regex_vserver_pattern = re.compile("INET_TEMP")


def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = "10.90.210.245"
    client.connect(
        hostname=host,
        username="sdi",
        password="ZJ2~H59!!"
    )
    return client


def checkVserver():
    list_name = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        # print "Connected to %s" % hostname
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
    list_name = []
    dict_name = {}
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
    except paramiko.AuthenticationException:
        return "Failed to connect to % s due to wrong username / password" % hostname
    except:
        return "Failed to connect to % s" % hostname
    try:
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
                print split_volume_name
                vserver_name = split_volume_name[0]
                volume_name = split_volume_name[1]
                if vserver_name == "INET-Temp-01" or vserver_name == "INET-Temp-02":
                    pass
                # else:
                #     print vserver_name, volume_name
                    # if not dict_name.has_key(vserver_name):
                    #     dict_name[vserver_name] =

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
        return "This is check volume function", True
    except Exception as e:
        # print "stop\n"
        return "A", True
        # return e.message


def createVolume(vserver, volume_name, size, aggregate_name):
    try:
        # print name
        # print type(name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        # print "Connected to %s" % hostname
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
        return "Create volume success"
    except Exception as e:
        # print e.message
        return "Create volume fail."


def getAggregate():
    result_list = []
    result_dict = {}
    try:
        # print name
        # print type(name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        # print "Connected to %s" % hostname
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
        # print name
        # print type(name)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        # print "Connected to %s" % hostname
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
    print real_volume_name
    print real_size
    build_volume = createVolume(vserver_name, real_volume_name, real_size, aggregate_name)
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

