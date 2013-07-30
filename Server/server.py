import sys
from socket import *
from time import sleep
import json

def broadcaster():
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.sendto('hello', ('<broadcast>', 50010))
    print('Broadcasting to network my IP')
    s.close()

def pinger(clientlist):
    if clientlist == []:
        print('No Pis to ping')
    else:
        message = 'bob'
        todelete = []
        #clientlist = ['10.0.5.173','10.5.2.3']
        print('Starting pinger. Addresses to ping = ' + str(clientlist))
        #print(clientlist)
        for clientnum in range(0,len(clientlist)):
            #print('Going round clientnum loop, on loop ' + str(clientnum))
            address = clientlist[clientnum]

            #print('About to ping')
            PORT = 50008             # The same port as used by the server
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(0.1)
            try:
            
                s.connect((address, PORT))
                s.sendall('Ping')
                #print('Sent, waiting for data')
                data = s.recv(1024)
                #print(data)
                
            
                s.close()
                #print('Socket closed')

            except error :
                #print('Socket timed out')
                todelete.append(clientnum)
                #print(clientlist)

        for delnum in range(0 ,len(todelete)+1):
            #print(str(todelete))
            #print(delnum)
            if delnum in todelete:
                del clientlist[delnum]
            

def datachecker(clientlist):
    print('')
    print('Waiting for incoming messages')
    s.settimeout(10) #Time between pings
    try:
        client, address = s.accept()
        sleep(0.1)
        data = client.recv(size)
        if data:
            if data == 'Register':
                if not (address in clientlist):
                    #print(address)
                    clientlist.append(str(address[0]))
                    print('')
                    print('-------------------------------------')
                    print('Client at ' + str(address[0]) +' added to list')
                    print('-------------------------------------')
                    print('')
                client.send('Accept')
                sleep(0.05)
            elif data == 'RequestList':
                tosendlist = json.dumps(clientlist)
                client.send(tosendlist)
            #print(data)
        client.close()
    except timeout:
        pass
        #print('Timeout')
    return clientlist
    

host = ''
port = 50000
backlog = 5
size = 1024
s = socket(AF_INET, SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
#clientlist = ['10.0.5.173','10.5.2.3']
s.settimeout(5)
clientlist = []
while 1:
    broadcaster()
    pinger(clientlist)
    clientlist = datachecker(clientlist)

