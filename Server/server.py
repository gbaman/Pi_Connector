import sys
from socket import *
from time import sleep
import traceback
import json
import sqlite3
import threading

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
                #print(data)
                
            
                s.close()
                #print('Socket closed')

            except error :
                #print('Socket timed out')
                todelete.append(clientnum)
                #print(clientlist)

        for delnum in range(0 ,len(todelete)+1):
            #print(str(todelete))
            #print(delnum)f
            if delnum in todelete:
                del clientlist[delnum]

class sender(threading.Thread):

    def __init__(self, sendlist, data):
        super(sender, self).__init__()
        self.sendlist = sendlist
        self.data = data
    def run(self):
        for client in range(0, len(self.sendlist)):
            try:
                self.send(self.sendlist[client], self.data)
            except:
                print("Command to "+ str(self.sendlist[client])+ " failed, commmand was " + str(self.data))
    def send(self, client, data):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(0.3)
        s.connect((client, 50008))
        s.sendall(data)
        s.close()

class ping(threading.Thread):

    def __init__(self):
        super(ping, self).__init__()
        self.pingFreq = 3

    def run(self):
        sql = sqlite3.connect('Pi-control.db')
        while True:
            self.pinger2(sql)
            sleep(self.pingFreq)

    def pinger2(self,sql):
        sqlp = sql.cursor()
        for row in sqlp.execute("""SELECT IP FROM ClientID"""):
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(0.3)
            try:
                s.connect((row[0], 50008))
                s.sendall('Ping')
                self.data = s.recv(1024)
                s.close()
            except error:
                sqlp.execute("""DELETE FROM ClientID WHERE IP = ?""", row)
                sql.commit()

class transmissionHandler(threading.Thread):
    def __init__(self, ip, data):
        super(transmissionHandler, self).__init__()
        print(ip)
        self.ip = ip
        self.data = data

    def run(self):
        sql = sqlite3.connect('Pi-control.db')
        self.TransHandler(self.ip, self.data, sql)
    def TransHandler(self, ip, data, sql):
        print("Handler called!!")
        self.interpreter(ip, data, sql)
    def interpreter(self, ip, data, sql):
        #print(data[0:4])
        if data[0:4] == "name":
            #print(data)
            self.name = (data.split(':'))[1]
            self.ip = (data.split(':'))[2]
            #data = data[1]
            #d = (self.name, self.ip)
            sqld = sql.cursor()
            #print(self.ip)
            sqld.execute("""SELECT Serial FROM ClientID WHERE Ip = ? """,(self.ip,) )
            #if sqld.fetchone() == None:
            #print(sqld.fetchone())
            d = (self.name, sqld.fetchone()[0])
            sqld.execute("""UPDATE Metadata SET Name = ? WHERE Serial = ?""",d)
            #print(d)
            sql.commit()
        sql.close()




def datachecker2(sql, sqlc):
    print('')
    print('Waiting for incoming messages')
    s.settimeout(10) #Time to wait before going onto next function
    try:
        client, address = s.accept()
        sleep(0.1)
        data = client.recv(size)
        if data:
            #print(data[0:7])
            print(data)
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
                    sqlc.execute("""SELECT Serial FROM Metadata WHERE Serial = ? """, (serial,))
                    if sqlc.fetchone() == None:
                        sqlc.execute("""INSERT INTO Metadata VALUES(?,NULL) """, (serial,))
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
                sqlc.execute("""SELECT ClientID.IP, ClientID.Serial, Metadata.Name
                            FROM ClientID
                            INNER JOIN Metadata
                            ON ClientID.Serial = Metadata.Serial""")
                tosendlist = sqlc.fetchall()
                client.send(json.dumps(tosendlist))
                print(tosendlist)
            else:
                print(address[0])
                t = transmissionHandler(address[0], data)
                t.daemon = True
                t.start()

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
Serial varchar(4) NOT NULL,
Name varchar(30)
)''')
    sqlc.execute("""CREATE  TABLE "main"."Connection" ("UserID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "IP" VARCHAR NOT NULL , "Key" INTEGER)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."Metadata" ("Serial" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE , "Name" VARCHAR)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."Group" ("GroupID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Name" VARCHAR NOT NULL , "Description" VARCHAR)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."GroupConnection" ("ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Serial" VARCHAR NOT NULL , "GroupID" INTEGER NOT NULL )""")
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

        p = ping()
        p.daemon = True
        p.start() #Starts the pinger thread


        while 1:
            broadcaster()
            #pinger(clientlist)
            #p.pinger2(sql,sqlc)
            #clientlist = datachecker(clientlist)
            datachecker2(sql,sqlc)
    except:
        print('************************************')
        print("System error...")
        traceback.print_exc(file=sys.stdout) #Prints out traceback error
        print('************************************')
        print("")
        print("Hit any key to proceed")
        raw_input()
        print("RESTARTING")
        sleep(3)

