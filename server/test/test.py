from host import Host
from node import Node
import validate
import json


def get_json_dict(host):
	return {
				"ip" : host.get_ip(),
				"nodes": 
						[
							{
								"id" : n.get_id(),
								"hardware": n.get_hardware(),
								"images" : n.get_images(),
								"usb" : n.get_usb(),
								"default_image" : n.get_default_image()
							} for n in host.get_nodes()
						]
			}

def get_json(hosts):
	return json.dumps({h.get_name() : get_json_dict(h) for h in hosts})

def get_node_list(nodes):
	node_list = []
	node_groups = nodes.split(',')
	for ng in node_groups:
		node_range = ng.split('-')
		if len(node_range) > 1:
			node_list.extend(list(range(int(node_range[0]),int(node_range[1])+1)))
		else:
			node_list.append(int(node_range[0]))
	return node_list


def read_file(filename):
	hardware_dict = {}
	node_dict = {}
	host_list = []
	hosts = []
	with open(filename, 'r') as f:
		for line in f:
			if line[0] == '-':
				break
			l = line.split()
			if l and line[0]!='#':
				hardware, images, usb = line.split()
				hardware_dict[hardware] = (images.split(','),usb)

		for line in f:
			if line[0] == '-':
				break
			l = line.split()
			if l and line[0]!='#':
				nodes, hardware, default = line.split()
				for n in get_node_list(nodes):
					node_dict[n] = (hardware if hardware != 'x' else '',default)
		for line in f:
			if line[0] == '-':
				break
			l = line.split()
			if l and line[0]!='#':
				name, ip, nodes = line.split()
				host_list.append((name,ip,get_node_list(nodes)))

	for h in host_list:
		hosts.append(Host(h[0],h[1]))
		for n in h[2]:
			hardware, default = node_dict[n]
			if hardware:
				images, usb = hardware_dict[hardware]
			else:
				images,usb = [],''
			hosts[-1].add_node(Node(n,hardware, default, images, usb))
	return hosts


hosts = read_file('machine.reference')
hosts = [ h for h in hosts if validate.validate(h)]
print json.dumps({h.get_name() : get_json_dict(h) for h in hosts}, sort_keys=True,indent=4, separators=(',', ': '))

# hosts = []
# h = Host('rack1', '192.168.0.11')
# h.add_node(Node(11,'usrp',['gnuradio','plain','lavras','openlte'],'2500:0020'))
# h.add_node(Node(21,'telosb',['telosb'],'0403:6001'))
# validate.validate(h)

# hosts.append(h)

# h3 = Host('rack3', '192.168.0.13')
# h3.add_node(Node(13,'usrp',['gnuradio','plain','lavras','openlte'],'2500:0020'))
# h3.add_node(Node(23,'telosb',['telosb'],'0403:6001'))
# validate.validate(h3)

# hosts.append(h3)
# # print json.dumps(get_json_dict(h), sort_keys=True,indent=4, separators=(',', ': '))
# # print json.dumps(get_json(h))

# print json.dumps({h.get_name() : get_json_dict(h) for h in hosts}, sort_keys=True,indent=4, separators=(',', ': '))