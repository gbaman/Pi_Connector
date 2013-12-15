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
            


def pinger2(sql, sqlc):
    for row in sqlc.execute("""SELECT IP FROM ClientID"""):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(0.3)
        try:
            s.connect((row[0], 50008))
            s.sendall('Ping')
            data = s.recv(1024)
            s.close()
        except error:
            sqlc.execute("""DELETE FROM ClientID WHERE IP = ?""", row)
            sql.commit()



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


def datachecker2(sql, sqlc):
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
                ip = (address[0],)
                print(str(ip))
                sqlc.execute("""SELECT CId, IP, Serial, Name FROM ClientID WHERE IP = ? """, ip)
                if sqlc.fetchone() == None:
                    datas = data.split(":")
                    serial = str(datas[1])
                    print(serial)
                    dat = (address[0], serial)
                    print(dat)
                    sqlc.execute("""INSERT INTO ClientID VALUES(NULL,?, ?, NULL)""", dat)
                    sql.commit()
                    print('')
                    print('-------------------------------------')
                    print('Client at ' + str(address[0]) +' added to list')
                    print('-------------------------------------')
                    print('')
                print("Data adding sorted")
                client.send('Accept')
                sleep(0.05)
            elif data == 'RequestList':
                sqlc.execute("""SELECT IP, Serial FROM ClientID""")
                tosendlist = sqlc.fetchall()
                client.send(json.dumps(tosendlist))
                print(tosendlist)

            client.close()
    except timeout:
        pass
    #except:
        #pass


def createDatabase(sqlc, sql):
    print("Creating database")
    sqlc.execute('''CREATE TABLE ClientID
(
CId INTEGER PRIMARY KEY AUTOINCREMENT,
IP varchar(15) NOT NULL,
Serial int(4) NOT NULL,
Name varchar(30)
)''')
    sqlc.execute("""CREATE  TABLE "main"."Connection" ("UserID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "IP" VARCHAR NOT NULL , "Key" INTEGER)""")
    #sql.commit()

def setupNetworking():
    host = ''
    port = 50000
    backlog = 5
    size = 1024
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)
    s.settimeout(5)
    return s


def InitalSQL(sql):

    sqlc = sql.cursor()
    try:
        sqlc.execute("""DROP TABLE "main"."ClientID" """)
    except:
        print("No database found, creating one")
    try:
        sqlc.execute("""DROP TABLE "main"."Connection" """)
    except:
        pass
    createDatabase(sql, sqlc)
    return sqlc


#**********************************************************- Main program - **********************************************************



while True:
    try:

        size = 1024
        s = setupNetworking()
        clientlist = []
        sql = sqlite3.connect('Pi-control.db')
        sqlc = InitalSQL(sql)


        while 1:
            broadcaster()
            #pinger(clientlist)
            pinger2(sql,sqlc)
            #clientlist = datachecker(clientlist)
            datachecker2(sql,sqlc)
    except (not KeyboardInterrupt):
        print('************************************')
        print("System error...")
        traceback.print_exc(file=sys.stdout) #Prints out traceback error
        print('************************************')
        print("")
        print("Hit any key to proceed")
        raw_input()
        print("RESTARTING")
        sleep(3)

