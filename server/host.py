from node import Node

class Host():
    
    def __init__(self, name, ip, user):
        self.name = name
        self.ip = ip
        self.user = user
        self.nodes = []

    def __repr__(self):
        return '%s,%s,%s'%(self.name,self.ip,str(self.nodes))

    def __str__(self):
        return '(%s : %s - '%(self.name,self.ip) + 'Nodes: ' + str(self.nodes) + ')'

    def get_name(self):
        return self.name

    def get_ip(self):
        return self.ip

    def get_user(self):
        return self.user

    def get_nodes(self):
        return self.nodes

    def add_node(self,node):
        assert isinstance(node, Node)
        self.nodes.append(node)

    def remove_node(self,node):
        assert isinstance(node, int)
        self.nodes = [n for n in self.nodes if n.get_id() != node]

    def clear_nodes(self):
        self.nodes = []