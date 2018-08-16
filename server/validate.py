import re
import subprocess
from platform import system as system_name # Returns the system/OS name 
import os

import node
import host

def check_ping(ip):
    """
    Returns True if host (str) responds to a ping request.
    Remember that some hosts may not respond to a ping request even if the 
    host name is valid.
    """

    ping_call = ['ping', '-n' if system_name().lower()=="windows" else '-c',
                '1',ip]

    # Pinging
    try:
        response = subprocess.check_output(
            ping_call,
            stderr=subprocess.STDOUT,  # get all output
            universal_newlines=True  # return string not bytes
        )
    except subprocess.CalledProcessError:
        response = None

    return response != None


def check_ssh(user,ip):
    """
    @brief      Checks if the node is reachable through SSH 
    
    @param      user  The node's user
    @param      ip    The node's IP address
    
    @return     Returns True if the SSH connection was possible, 
                False otherwise 
    """

    ssh_call = ['ssh', '-o', 'ConnectTimeout=10', '-t', user+'@'+ip, 'exit']
    try:
        response = subprocess.check_output(
            ssh_call,
            stderr=subprocess.STDOUT,  # get all output
            universal_newlines=True  # return string not bytes
        )
    except subprocess.CalledProcessError:
        response = None

    return response != None


def check_libvirt(user, ip):
    """
    @brief      Checks if libvirt is up and running on the node
    
    @param      user  The node's user
    @param      ip    The node's IP address
    
    @return     Returns True if the libvirt service is running on the machine,
                False otherwise
    """

    HOST = user+'@'+ip
    COMMAND = 'service libvirtd status | grep Active'
    with open(os.devnull, 'w') as devnull:
        ssh = subprocess.Popen(['ssh','-o','UserKnownHostsFile=/dev/null','-o',
            'StrictHostKeyChecking=no','-t', '%s' % HOST, COMMAND],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=devnull)
        out = ssh.stdout.read()
    return 'Active: active (running)' in out


def check_hardware(host):
    """
    @brief      Checks if the host machine has the correct hardware 
                attached to it
    
    @param      host  The host object
    
    @return     Returns True if after the checking, the host machine has any
                nodes attached to it. If not, it means that no hardware was
                identified attached to the machine, then the method 
                returns False.
    """

    try:
        nodes = host.get_nodes()
        host.clear_nodes()
        for n in nodes:
            if n.get_hardware() and n.get_usb():
                if check_usb(host.get_user(),host.get_ip(),n.get_usb()):
                    host.add_node(n)
            else:
                host.add_node(n)
    except Exception as e:
        print('ERROR: ' + str(e))
    finally:
        return host.get_nodes() != []


def check_usb(user,ip,usb):
    """
    @brief      Checks if the USB device is attached to the machine and 
                identified by the system.
    
    @param      user  The machine's user
    @param      ip    The machine's IP address
    @param      usb   The USB device Vendor and Product, as a string
    
    @return     Returns true if the command 'lsusb' returned a device with the
                vendor and product specified in the 'usb' variable.
    """

    HOST = user+'@'+ip
    COMMAND = 'lsusb | grep '+usb
    with open(os.devnull, 'w') as devnull:
        ssh = subprocess.Popen(['ssh','-o','UserKnownHostsFile=/dev/null','-o',
            'StrictHostKeyChecking=no','-t', '%s' % HOST, COMMAND],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=devnull)
        out = ssh.stdout.read()
    
    return ('ID '+usb) in out



def has_error(host):
    """
    @brief      Checks for error in each host.
    
    @param      host  The host object
    
    @return     Error code. 0 for no error. 1 for ping error. 2 for ssh error.
                3 for libvirt error. 4 for hardware error.
    """

    name = host.get_name()
    ip = host.get_ip()
    user = host.get_user()

    matched_obj = re.match("([a-zA-Z]+)([0-9]+)",host.get_name())

    host_type = matched_obj.group(1)

    error = 0
    try:
        valid = False
        if check_ping(ip):
            if check_ssh(user,ip):
                if host_type == 'rack':
                    if check_libvirt(user,ip):
                        if check_hardware(host):
                            valid = True
                        else:
                            error = 4
                    else:
                        error = 3
                elif host_type == 'rasp':
                    valid = True
            else:
                error = 2
        else:
            error = 1
    except KeyboardInterrupt:
        print('\nFinishing')
    except Exception as e:
        print e
    finally:
        return error


def validate(host):
    """
    @brief      Validates the machine's status through the "has_error' method.
    
    @param      host  The host object
    
    @return     True if no error. False otherwise.
    """

    error_msg = has_error(host)
    print host.get_name() + ': ',
    if not error_msg:
        print('ok')
        return True
    elif error_msg == 1:
        print('ping fail')
    elif error_msg == 2:
        print('ssh fail')
    elif error_msg == 3:
        print('libvirt fail')
    elif error_msg == 4:
        print('hardware fail')

    return False
