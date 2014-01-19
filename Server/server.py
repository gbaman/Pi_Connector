import sys
from socket import *
from time import sleep
import traceback
import json
import sqlite3
import threading
import random

def broadcaster():
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.sendto('hello', ('<broadcast>', 50010))
    print('Broadcasting to network my IP')
    s.close()

class sender(threading.Thread):

    def __init__(self, sendlist, data, port = 50008):
        super(sender, self).__init__()
        self.sendlist = sendlist
        self.data = data
        self.dport = port
    def run(self):
        for client in range(0, len(self.sendlist)):
            try:
                self.send(self.sendlist[client], self.data)
            except:
                print("Command to "+ str(self.sendlist[client])+ " failed, commmand was " + str(self.data))
    def send(self, client, data):
        print("sending " + str(client) + " " + str(data))
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(0.3)
        print("Connecting to client at " +str(client) + " " + str(self.dport))
        s.connect((client, self.dport))
        s.sendall(json.dumps((data,)))
        s.close()
        print("Data is sent!")

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
                s.sendall(json.dumps(('Ping',)))
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
        level = checkToken(self.data[2])
        self.interpreter(ip, data, level, sql)
    def interpreter(self, ip, data, level, sql):
        #print(data[0])
        print(data)
        if (data[0] == "name") and (level >1):
            #print(data)
            self.name = (data[1][0])
            self.ip = (data[1][1])
            print("IP is " + str(self.ip) + " Name is " + str(self.name))
            #data = data[1]
            #d = (self.name, self.ip)
            sqld = sql.cursor()
            #print(self.ip)
            sqld.execute("""SELECT Serial FROM WHERE Ip = ? """,(self.ip,) )
            #if sqld.fetchone() == None:
            #print(sqld.fetchone())
            d = (self.name, sqld.fetchone()[0])
            sqld.execute("""UPDATE Metadata SET Name = ? WHERE Serial = ?""",d)
            #print(d)
            sql.commit()
            sql.close()

def randomDigits(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    toreturn = random.randint(lower, upper)
    print("Hash generated is " + str(toreturn))
    return toreturn

def decodeHash(hash, password):
    print("At hash, hash is " + str(hash) + " and password is " + str(password))
    if hash == password:
        return True
    else:
        return False

def getToken(credentials, sql, sqlc):
    username = (credentials[0],)
    sqlc.execute("""SELECT UserID, Username, Salt, Hash, PermissionLevel, Token FROM User WHERE Username = ? """, username)
    fetch = sqlc.fetchone()
    print(str(fetch))
    if not (fetch == None):
        sqlc.execute("""SELECT Hash FROM User WHERE Username = ? """, username)
        hash = sqlc.fetchone()
        if (decodeHash(hash[0], credentials[1])) == True:
            return randomDigits(10)
        else:
            return False
    else:
        return False

def checkToken(token):
    sqls = sqlite3.connect('Pi-control.db')
    sqld = sqls.cursor()
    token = (token, )
    sqld.execute("""SELECT PermissionLevel FROM User WHERE Token = ? """, token)
    result = sqld.fetchone()
    if not (result == None):
        print(str(result))
        return result[0]
    else:
        return 0



def getPermission(user):
    pass


def datachecker2(sql, sqlc):
    print('')
    print('Waiting for incoming messages')
    s.settimeout(10) #Time to wait before going onto next function
    try:
        client, address = s.accept()
        sleep(0.1)
        data = client.recv(size)
        if data:
            data = json.loads(data)
            #print("Raw data")
            #print(data)
            #print(data[0:7])
            #print(data)
            if (data[0] == 'Register'):
                ip = (address[0],)
                #print(str(ip))
                sqlc.execute("""SELECT CId, IP, Serial FROM ClientID WHERE IP = ? """, ip)
                if sqlc.fetchone() == None:
                    #datas = data.split(":")
                    serial = str(data[1])
                    #print(serial)
                    dat = (address[0], serial)
                    #print(dat)
                    sqlc.execute("""INSERT INTO ClientID VALUES(NULL,?, ?)""", dat)
                    sqlc.execute("""SELECT Serial FROM Metadata WHERE Serial = ? """, (serial,))
                    if sqlc.fetchone() == None:
                        sqlc.execute("""INSERT INTO Metadata VALUES(?,NULL) """, (serial,))
                    sql.commit()
                    print('')
                    print('-------------------------------------')
                    print('Client at ' + str(address[0]) +' added to list')
                    print('-------------------------------------')
                    print('')
                #print("Data adding sorted")
                client.send(json.dumps(('Accept',)))
                sleep(0.05)

            elif data[0] == "Token":
                credentials = data[1]
                ip = (address[0],)
                result = getToken(credentials, sql, sqlc)
                if not (result == False):
                    d = (result, credentials[0])
                    print(str(d))
                    sqlc.execute("""UPDATE "main"."User" SET "Token" = ? WHERE  "Username" = ?""", d)
                    sql.commit()
                    #sqlc.execute("""UPDATE User SET Token = ? WHERE Username = ?""",d)
                else:
                    result = 0
                client.send(json.dumps((result,)))

            else:
                if (checkToken(data[2]) > 0):
                    if data[0] == 'RequestList':
                        sqlc.execute("""SELECT ClientID.IP, ClientID.Serial, Metadata.Name
                                    FROM ClientID
                                    INNER JOIN Metadata
                                    ON ClientID.Serial = Metadata.Serial""")
                        tosendlist = sqlc.fetchall()
                        client.send(json.dumps((tosendlist,)))
                        #print('sending list! ' + str(tosendlist))
                    else:
                        print(address[0])
                        t = transmissionHandler(address[0], data)
                        t.daemon = True
                        t.start()

                    client.close()
                else:
                    print("Invalid login")
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
Serial varchar(4) NOT NULL
)''')
    sqlc.execute("""CREATE  TABLE IF NOT EXISTS "main"."Connection" ("UserID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "IP" VARCHAR NOT NULL , "Key" INTEGER)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."Metadata" ("Serial" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE , "Name" VARCHAR)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."Group" ("GroupID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Name" VARCHAR NOT NULL , "Description" VARCHAR)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."GroupConnection" ("ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Serial" VARCHAR NOT NULL , "GroupID" INTEGER NOT NULL )""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."User" ("UserID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Username" VARCHAR NOT NULL , "Salt" VARCHAR NOT NULL , "Hash" VARCHAR NOT NULL , "PermissionLevel" INTEGER NOT NULL, "Token" INTEGER )""")
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

