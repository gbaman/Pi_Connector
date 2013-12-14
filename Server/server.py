import sys
from socket import *
from time import sleep
import traceback
import json
import sqlite3

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
            address = (clientlist[clientnum][0])

            #print('About to ping')
            PORT = 50008             # The same port as used by the server
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(0.3)
            try:
            
                s.connect((address, PORT))
                s.sendall('Ping')
                #print('Sent, waiting for data')
                data = s.recv(1024)
                print(data)
                
            
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
    s.settimeout(10) #Time to wait before going onto next function
    try:
        client, address = s.accept()
        sleep(0.1)
        data = client.recv(size)
        if data:
            print(data[0:7])
            if data[0:8] == 'Register':
                exist = False
                for count in range(0, len(clientlist)):
                    if (address in clientlist[count]):
                        exist = True
                if exist == False:
                    #print(address)
                    datas = data.split(":")
                    serial = datas[1]
                    print(str(serial))
                    clientlist.append([str(address[0]),  serial])
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

def createDatabase(sqlc, sql):
    print("Creating database")
    sqlc.execute('''CREATE TABLE ClientID
(
CId int NOT NULL,
IP varchar(15) NOT NULL,
Serial int(4) NOT NULL,
Name varchar(30),
PRIMARY KEY (CId)
)''')
    #sql.commit()


while True:
    try:

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
        sql = sqlite3.connect('Pi-control.db')
        sqlc = sql.cursor()
        stmt = "SHOW TABLES LIKE 'ClientID'"
        sqlc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ClientID';")
        result = ""
        result = sqlc.fetchone()
        print(str(result))
        if (result) == None:
            createDatabase(sql, sqlc)
        while 1:
            broadcaster()
            pinger(clientlist)
            clientlist = datachecker(clientlist)
    except:
        print('************************************')
        print("System error...")
        traceback.print_exc(file=sys.stdout)
        print('************************************')
        print("")
        print("Hit any key to proceed")
        raw_input()
        print("RESTARTING")
        sleep(3)

