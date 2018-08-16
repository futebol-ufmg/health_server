#!/usr/bin/env python
import threading
import time
from host import Host
from node import Node
from validate import validate
import json

class MonitorDaemon():
    """ Daemon class for monitoring testbed status.

    This class is designed to act as a daemon, monitoring the status of the 
    testbed's nodes and hosts.
    """

    def __init__(self, filename='machine.reference',time=30):
        self.filename = filename
        self.time = time
        self.stopFlag = threading.Event()
        self.update_lock = threading.Lock()

        self.update()

        self.back = threading.Thread(target = self.background_update)
        self.back.start()


    def shutdown(self):
        self.stopFlag.set()
        self.back.join()
        print('Shutting down monitor')



    def _read_file(self,filename):
        """ Parse the machine.reference file.

        This method parses the machine.reference file, obtaining and storing
        information about available hosts and nodes in the testbed.
        
        Arguments:
            filename {str} -- Name of the file.
        
        Returns:
            hosts {list} -- a list of hosts that should be available on 
            the testbed, according to the file.
        """
        def get_node_list(nodes):
            """ Build a list containing the nodes numbers.

            Given the string passed as parameter, this method builds a list of
            node numbers, comprehensive of ranges in the string.
            
            Arguments:
                nodes {str} -- string containing the numbers of nodes declared
                in the file.
            
            Returns:
                node_list {list} -- list of node numbers.
            """
            node_list = []
            node_groups = nodes.split(',')
            for ng in node_groups:
                node_range = ng.split('-')
                if len(node_range) > 1:
                    #Expand ranges (sequentially) found in the string
                    #e.g. 1-5 turns into [1,2,3,4,5]
                    node_list.extend(list(range(int(node_range[0]),
                                                int(node_range[1])+1)))
                else:
                    #Append single nodes
                    node_list.append(int(node_range[0]))
            return node_list

        hardware_dict = {}
        node_dict = {}
        host_list = []
        hosts = []
        with open(filename, 'r') as f:
            #Read first section of file (machine.reference)
            for line in f:
                #Stop at the end of section
                if line[0] == '-':
                    break
                l = line.split()
                if l and line[0]!='#': #Ignore comments and empty lines
                    hardware, images, usb = line.split()
                    #Hardware dict is built as a dictionary with the hardware 
                    #name as key, the images names and the USB ID for the 
                    #device as values 
                    hardware_dict[hardware] = ( images.split(','),
                                                usb if usb != 'x' else '')

            #Read second section of file (machine.reference)
            for line in f:
                #Stop at the end of section
                if line[0] == '-':
                    break
                l = line.split()
                if l and line[0]!='#': #Ignore comments and empty lines
                    nodes, hardware, default, raw = line.split()
                    for n in get_node_list(nodes):
                        #Node dic is built as a dictionary with the node number
                        #as key, the hardware, default image name and a boolean
                        #value indicating if the node is a raw node or not
                        #as values
                        node_dict[n] = (hardware if hardware != 'x' else '',
                                        default,
                                        raw.lower() == 'true')
            #Read third section of file (machine.reference)
            for line in f:
                #Stop at the end of section
                if line[0] == '-':
                    break
                l = line.split()
                if l and line[0]!='#': #Ignore comments and empty lines
                    name, ip, user, nodes = line.split()
                    #Add a tuple containing information about the host to the
                    #host list            
                    host_list.append((name, ip, user, get_node_list(nodes)))


        for h in host_list:
            #Iterate through hosts list adding Host objects, and filling them 
            #with node information
            hosts.append(Host(h[0],h[1],h[2]))
            for n in h[3]:
                hardware, default, raw = node_dict[n]
                if hardware:
                    images, usb = hardware_dict[hardware]
                else:
                    images,usb = [],''
                hosts[-1].add_node(Node(n, hardware, default, images, usb, raw))
        #Return list of Host objects
        return hosts

    def update(self):
        print('Updating Resources')

        hosts = self._read_file(self.filename)

        hosts = [ h for h in hosts if validate(h)]

        with self.update_lock:
            self.hosts = hosts
        print('Resources Updated:')
        print(self.get_resources())


    def background_update(self):
        while not self.stopFlag.wait(self.time):
            self.update()


    def _get_json_dict(self, host):
        return {
                    "ip" : host.get_ip(),
                    "user" : host.get_user(),
                    "nodes":
                            [
                                {
                                    "id" : n.get_id(),
                                    "hardware": n.get_hardware(),
                                    "images" : n.get_images(),
                                    "usb" : n.get_usb(),
                                    "default_image" : n.get_default_image(),
                                    "raw" : n.is_raw()
                                } for n in host.get_nodes()
                            ]
                }

    def get_resources(self):

        with self.update_lock:
            hosts = self.hosts

        return json.dumps({h.get_name():self._get_json_dict(h) for h in hosts})
