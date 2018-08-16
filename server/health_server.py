#!/usr/bin/env python
''' 
Copyright (c)  2016 The Provost, Fellows and Scholars of the
College of the Holy and Undivided Trinity of Queen Elizabeth near Dublin.
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from monitor_daemon import MonitorDaemon
import base64
import zlib

class ConnectionFactory(Factory):
    def __init__(self, pointer):
        self.requests = {}
        self.get_resources = pointer

    def startFactory(self):
        print('Starting Connection Factory')

    def stopFactory(self):
        print('Stoping Connection Factory')

    def run_server(self, port):
        reactor.listenTCP(port, self)
        reactor.run()

    def buildProtocol(self, addr):
        return HealthProtocol(self.get_resources)

class HealthProtocol(Protocol):
    ''' 
        This class is responsible for adapting the TCP server for the usage of
        the CBTP, establishing communication between the Server and a Client
    '''

    def __init__(self, pointer):
        self.get_resources = pointer


    def send_response(self, msg):
        ''' 
            Receive messages from the Handler and send it back to the client.
        '''
        print('Sending: "%s" to %s'%(msg, str(self.peer)))
        self.transport.write(('00'+str(len(msg)))[-3:]+msg)
        self.transport.loseConnection()

    def connectionMade(self):
        ''' 
            Capture connections to the server.
        '''
        self.peer = self.transport.getPeer()
        print('New connection from %s'%str(self.peer))

    def dataReceived(self, rx_data):
        ''' 
            Receive data from the client and send it to the Handler.
        '''
        data = rx_data.strip()
        #self.log.debug('Received "%s" from %s'%(data, str(self.peer)))
        print('Received "%s" from %s'%(data, str(self.peer)))

        command = data.split(':')
        origin = command.pop(0)

        msg = self.handler(origin, command)
        self.send_response(msg)


    def handler(self, origin, command):
        if origin == 'AM':
            print('Connection from AM')
        elif origin == 'CO':
            print('Connection from Coordinator')
        elif origin == 'CB':
            print('Connection from CBTM')
        elif origin == 'HM':
            print('Other origin')

        msg = ''
        if command[0] == 'gr':
            msg = self.get_resources()

        return base64.b64encode(zlib.compress(msg))



if __name__ == '__main__':
    port = 4000
    try:
        monitor = MonitorDaemon()

        server = ConnectionFactory(monitor.get_resources)
        server.run_server(port)
    except Exception as e:
        print e
        raise e
    finally:
        monitor.shutdown()

