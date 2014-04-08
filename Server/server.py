#!/usr/bin/python
import sys
from socket import *
from time import sleep
import traceback
import json
import sqlite3
import threading
import hashlib
import random
from logging import debug, info, warning, basicConfig, INFO, DEBUG, WARNING

basicConfig(level=WARNING)

#Protocols
"""
Menu drawing - (Reserved, String, IP, Response?, Response_Command, Token?, Secondary_response, Local, Reserved)
Standard communication - (Message, (Payload), Token)
Server relay communications - (Relay, (Message, (Payload)), Token, (Recipients)
Server communications - ("Server", (Message, (Payload)), Token, (Recipients)

Menu
0. Reserved - A reserved character
1. String - The string displayed on the client side
2. IP - Who is the message being set to? Constants = pi, server. Or just the direct IP address
3. Response? - Does the user need to fill in some extra information?
4. Command sent to the server to run the instruction
5. Token?
6. Secondary_response - Does the client need to wait for a reply?
7. Local - Is it a command only for the local user, it will use the client IP address
8. Reserved


To create a command
First define its permission level in __init__

Next, pick which menu your object must be part of. If it is due to be part of the main home menu, put your function in homeMenuBuild
If it is to be part of the Pi menu (which most will be), place it in mainBuild. These are functions that will be available for that specific Raspberry Pi.

To create a function, follow the menu protocol above.

Here is an example
        if self.shutdown <= level: #First checks if the user has permission
            value = ("", "Shutdown", "pi", False, "Shutdown", True, "None", False, "" ) #If the user does, now builds the item. The first shutdown is what appears on their screen, pi is there as it is
            self.menu.append(value) #due to be run on a pi, as opposed to the server ("server" is also available"). Finally, the menu being sent is appended with this new information.

A few things to be awear of, there are some special situations.
Special situations
1. For the IP addresses in homeMenuBuild, the String item (item 1), is actually another list, [Ip address, name]. Do not make use of name as it is removed clientside after it is displayed and reverted to just [ip address]
2. Many functions have 2 permission levels, e.g. self.shutdown and self.localshutdown. If the user has permission for self.shutdown, because of the elif, local shutdown will never appear. If they dont, it will appear.
3. There are some hardcoded in functions at the other end, stuff like "exit" which will just run homeMenuBuild. Refresh does the same thing.
4. "ClientMenu" will load clientMenu on the clientside, aka loading a menu for a specific IP address
5. If a command is meant to go out to "all", then the ip object [2] changes to a sublist, ["all", "pi or server"]. Later the "all" is stipped away leaving only the object in [1].

Pi Side. For all these functions, if it is being added to the pi, add it to interpreter function. For example, if your function sent over the word "Reboot", on pi side you would need
if data[0] == 'Reboot':
    call(['sudo', 'reboot'])
"call" runs a command in the shell of the pi.

Server Side. To add a function that is run serverside, it must be added in class transmissionHandler. In this class, there is an interpreter function.
Very similarly to the Pi side, just check if the string coming in is equal to what you expect. e.g. for "FeatureList"
if (data[0] == "FeatureList"):
    Do something



"""




class clientMenu(threading.Thread): #Class that controls menu drawing for textclient

    def __init__(self, ip, level, menuOpt = "Main", clientList = ""):
        super(clientMenu, self).__init__()
        self.menu =[]
        self.ipMenu = []
        self.ip = ip
        self.level = level
        self.menuOpt = menuOpt
        self.clientList = listit(clientList)

        #-------------------------------- Home menu
        self.refresh = 0
        self.allShutdown = 2
        self.allReboot = 2
        self.allGPIO = 2
        self.allScreenShare = 2
        self.allBlankScreen = 2
        self.allUnblankScreen = 2
        self.allSendCommand = 2



        self.viewAccessAllPis = 2
        self.viewMyPi = 1
        self.uploadFile = 1
        self.changePassword = 1



        #-------------------------------- Client menu

        self.exit = 0
        self.shutdown = 2
        self.localShutdown = 1
        self.reboot = 2
        self.localReboot = 1
        self.scratch = 1
        self.assignName = 2
        self.localLED = 1
        self.LED = 2
        self.GPIO = 2
        self.addToGroup = 2
        self.resetPassword = 2
        self.sendCommand = 2
        self.blankScreen = 2
        self.unblackScreen = 2

        #--------------------------------

    def run(self): #Starts here
        if self.menuOpt == "Main":
            self.sendMainMenu(self.mainBuild(self.level)) #If its a main menu request
        elif self.menuOpt == "Home":
            self.sendHomeMenu(self.homeMenuBuild(self.level)) #If its a home meny request



# Menu drawing - (Reserved, String, IP, Response?, Response_Command, Token?, Secondary_response, Local, Reserved)
    def mainBuild(self, level): # Builds the client menu
        debug("Level is " + str(level))

        if self.shutdown <= level:
            value = ("", "Shutdown", "pi", False, "Shutdown", True, "None", False, "" )
            self.menu.append(value)

        elif self.localShutdown <= level:
            value = ("", "Shutdown my Pi", "pi", False, "Shutdown", True, "None", True, "" )
            self.menu.append(value)

        if self.reboot <= level:
            value = ("", "Reboot", "pi", False, "Reboot", True, "None", False, "" )
            self.menu.append(value)

        elif self.localReboot <= level:
            value = ("", "Reboot my Pi", "pi", False, "Reboot", True, "None", True, "" )
            self.menu.append(value)

        if self.assignName <= level:
            value = ("", "Assign a name to this Pi", "server", "Please enter a new name", "name", True, "None", False, "" )
            self.menu.append(value)

        if self.sendCommand <= level:
            value = ("", "Send command this pis", "pi", "Enter command", "BatchCommand", True, "None", False, "" )
            self.menu.append(value)

        if self.blankScreen <= level:
            value = ("", "Lock screen", "pi", False, "ScreenLock", True, "None", False, "" )
            self.menu.append(value)

        if self.shutdown <= level:
            value = ("", "Unlock screen", "pi", False, "ScreenUnlock", True, "None", False, "" )
            self.menu.append(value)

        if self.exit <= level:
            value = ("", "Exit", "Exit", False, "Exit", True, "None", True, "" )
            self.menu.append(value)

        return self.menu

#------------------------------------------------------------------------------------------------------------------------

    def sendMainMenu(self, menuList):
        sleep(0.3)
        s = sender((self.ip,), ("MenuDraw", menuList, "1"), 50010, 1)
        s.run()
                                                    #Stars the sender threads
    def sendHomeMenu(self, menuList):
        sleep(0.3)
        s = sender((self.ip,), ("HomeDraw", menuList, "1"), 50009, 1)
        s.run()

#------------------------------------------------------------------------------------------------------------------------

    def homeMenuBuild(self, level): #Builds the home menu (first one user sees)
        debug("Level is " + str(level))

        if self.refresh <= level:
            value = ("", "Refresh", "pi", False, "Refresh", True, "None", False, "" )
            self.menu.append(value)

        if self.allShutdown <= level:
            value = ("", "Shutdown all Pis", ["all", "pi"], False, "Shutdown", True, "None", False, "" )
            self.menu.append(value)

        if self.allReboot <= level:
            value = ("", "Reboot all Pis", ["all", "pi"], False, "Reboot", True, "None", False, "" )
            self.menu.append(value)

        if self.allBlankScreen <= level:
            value = ("", "Lock all screens", ["all", "pi"], False, "ScreenLock", True, "None", False, "" )
            self.menu.append(value)

        if self.allUnblankScreen <= level:
            value = ("", "Unlock all screens", ["all", "pi"], False, "ScreenUnlock", True, "None", False, "" )
            self.menu.append(value)

        if self.allSendCommand <= level:
            value = ("", "Send command to all pis", ["all", "pi"], "Enter command", "BatchCommand", True, "None", False, "" )
            self.menu.append(value)

        if self.changePassword <= level:
            value = ("", "Change your password", "server", "Please enter your new password", "Password", True, "None", False, "" )
            self.menu.append(value)

        for count in range(0, len(self.clientList)):
            #print("self.clientList[count][2] is " + str(self.clientList[count][2]))
            #print(count)
            #print(self.clientList)
            if self.clientList[count][2] == None:
                self.clientList[count][2] = ""

            if (self.viewAccessAllPis <= level):
                if (self.ip == self.clientList[count][0]): #If the client running on this Raspberry Pi?
                    value = ("", [self.clientList[count][0],self.clientList[count][2] + " - *"] , "ClientMenu", False, "ClientMenu", True, "None", False, "" )
                else: #If the client isnt owned by this user
                    value = ("", [self.clientList[count][0],self.clientList[count][2]], "ClientMenu", False, "ClientMenu", True, "None", False, "" )
                self.ipMenu.append(value)
            elif (self.viewMyPi <= level) and (self.ip == self.clientList[count][0]): #If the user is a student and only has access to his/her Raspberry Pis.
                value = ("", [self.clientList[count][0],self.clientList[count][2] + " - *"] , "ClientMenu", False, "ClientMenu", True, "None", False, "" )
                self.ipMenu.append(value)
            else:
                debug("My self ip is " + self.ip + " and clientlistIP is " + self.clientList[count][0])

        if self.uploadFile <= level:
            value = ("", "Submit a file", "local", False, "GetFile", True, "None", False, "" )
            self.menu.append(value)

        if self.exit <= level:
            value = ("", "Quit", "ExitAll", False, "ExitAll", True, "None", True, "" )
            self.menu.append(value)


        debug("Menu now built, it is")
        totalMenu = [self.menu, self.ipMenu]
        debug(totalMenu)
        return totalMenu


class broadcaster(threading.Thread): #Class that controls the network broadcasts to allow clients to find the server
    def __init__(self):
        super(broadcaster, self).__init__()

    def run(self):
        while True:
            self.broadcaster()  #Broadcast to network
            sleep(2) #Wait 2 seconds before broadcasting again

    def broadcaster(self):
        s = socket(AF_INET, SOCK_DGRAM) #UDP socket
        s.bind(('', 0)) #Binds to localhost
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto('hello', ('<broadcast>', 50011)) #Network broadcast
        info('Broadcasting to network my IP')
        s.close()
class console(threading.Thread):

    def __init__(self):
        super(console, self).__init__()
    def run(self):
        while True:
            consoleMessage()
            try:
                response = raw_input()
                response = response.lower()
            except:
                print("Invalid input")
                sleep(1.5)
                continue
            if response == "c":
                response = ""
                self.cMenu()
            else:
                print("Invalid input")
                sleep(1.5)

    def sort(self, array):
        less = []
        equal = []
        greater = []

        if len(array) > 1:
            pivot = array[0]
            for x in array:
                if x < pivot:
                    less.append(x)
                if x == pivot:
                    equal.append(x)
                if x > pivot:
                    greater.append(x)
            return self.sort(less)+self.sort(equal)+self.sort(greater)
        else:
            return array



    def cMenu(self): #Main menu for user management
        sqlU = sqlite3.connect('Pi-control.db')
        sqlUc = sqlU.cursor()
        notdone = True
        while notdone:
            print("\n" * 5)
            print("Server Console menu")
            print("-------------------")
            print("")
            print("1. Add new user")
            print("2. Delete user")
            print("3. Modify user permission")
            print("4. Display all users and their permissions")
            print("5. Reset a users password")
            print("6. Disable user token to allow multiple simultaneous logins")
            print("7. Return to main screen")
            answer = raw_input()
            if answer == "1":
                self.newUser(sqlU, sqlUc)
            elif answer == "2":
                self.displayUsers(sqlU, sqlUc)
                self.deleteUser(sqlU, sqlUc)
            elif answer == "3":
                self.modifyPerms(sqlU, sqlUc)
            elif answer == "4":
                self.displayUsers(sqlU, sqlUc, True)
            elif answer == "5":
                self.resetPassword(sqlU, sqlUc)
            elif answer == "6":
                self.setTokenStatus(sqlU,sqlUc)
            elif answer == "7":
                notdone = False
            else:
                print("That is not a valid option")
                wait()
        consoleMessage()



    def newUser(self, sqlU, sqlUc):
        print("\n" * 5)
        correct = False
        while correct == False:
            username = (raw_input("Enter new username : ")).lower()
            password1 = raw_input("Enter password : ")
            password2 = raw_input("Enter password : ")
            level = raw_input("Enter permission level (1-3) : ")
            if len(password1) < 3:
                print("Password must be at least 3 characters long!")
                wait()
                continue
            if not (password1 == password2):
                correct = False
                print("Passwords must match, try again")
                wait()
                continue
            else:
                correct = True
                usernamex = (username, )
                sqlUc.execute("""SELECT UserID, Username, Salt, Hash, PermissionLevel, Token FROM User WHERE Username = ? """, usernamex) #Checks to see if the user already exists
                result = sqlUc.fetchone()
                if result == None: #If it does not already exits
                    hashresult = createHash(password1) #Creates hash, returns hash and salt
                    debug((username, hashresult[0], hashresult[1], level))
                    sqlUc.execute("""INSERT INTO User VALUES(NULL,?,?,?,?, NULL, NULL)""", ((username, str(hashresult[0]), str(hashresult[1]), level))) #Creates new user
                    sqlU.commit()
                    print("User " + str(username) + " has been successfully added")
                    wait()
                else:
                    print("")
                    print("Username already exists!")
                    wait()
                    break


    def displayUsers(self, sqlU, sqlUc, delay = False): #Displays all users, has a default delay paramater set to false.
        sqlUc.execute("""SELECT UserID, Username, PermissionLevel FROM User""")
        table = sqlUc.fetchall()
        print("ID : Name - Permission level")
        print("-----------------------")
        for count in range(0, len(table)):
            #print(str(table[count]))
            print(str(table[count][0]) + " : " + str(table[count][1]) + " - " + str(self.userperm(table[count][2])))
        if delay:
            wait()


    def checkIfUserExists(self, sqlU, sqlUc, cID, searchby = "UserID", display = False):
        cID = ((cID, ))
        debug(str(cID))
        sqlUc.execute("""SELECT UserID, Username FROM User WHERE UserID = ? """, cID)
        result = sqlUc.fetchone()
        if result == None:
            return False
        else:
            print("---------------------------------")
            print(result[1])
            print("---------------------------------")
            return True


    def deleteUser(self, sqlU, sqlUc):
        print("Enter the ID to delete")
        cID = raw_input()
        if self.checkIfUserExists(sqlU, sqlUc, cID, "UserID", True):
            print("Are you sure you want to remove this user? Type yes or no")
            user = raw_input().lower()
            if user == "yes":
                users = ((int(cID), ))
                sqlUc.execute("""DELETE FROM User WHERE UserID = ? """, users)
                sqlU.commit()
                print("User successfully deleted")
                wait()
            else:
                print("Operation canceled")
                wait()
        else:
            print("User does not exist")
            wait()


    def resetPassword(self, sqlU, sqlUc):
        self.displayUsers(sqlU, sqlUc)
        print("Enter User ID to reset the password of")
        cID = raw_input()
        if self.checkIfUserExists(sqlU, sqlUc, cID):
            print("Please enter a password to set it to")
            print("To cancel, leave blank")
            password = raw_input()
            if not (password == ""):
                if len(password) < 3:
                    print("Error, password must be at least 3 characters!")
                    wait()

                else:
                    hashresult = createHash(password)
                    sqlUc.execute("""UPDATE "main"."User" SET "Salt" = ?, "Hash" = ? WHERE  "UserID" = ?""",(str(hashresult[0]), str(hashresult[1]), int(cID)))
                    sqlU.commit()
                    print("Password successfully changed")
                    wait()
            else:
                print("Operation canceled")
                wait()
        else:
            print("User not found")
            wait()

    def setTokenStatus(self, sqlU, sqlUc):
        self.displayUsers(sqlU, sqlUc)
        print("Enter User ID to disable tokens with")
        cID = raw_input()
        if self.checkIfUserExists(sqlU, sqlUc, cID):
            sqlUc.execute("""UPDATE "main"."User" SET "NoToken" = ? WHERE  "UserID" = ?""",(True, int(cID)))
            sqlU.commit()
            print("User updated")
            wait()
        else:
            print("User not found")
            wait()

    def userperm(self, value):
        value = str(value)
        if value == "1":
            return "Student"
        elif (value == "2"):
            return "Teacher"
        elif value == "3":
            return "Admin"
        else:
            return "Unknown.."


    def modifyPerms(self, sqlU, sqlUc):
        self.displayUsers(sqlU, sqlUc)
        print("Please enter a user ID to modify permissions of")
        cID = raw_input()
        if self.checkIfUserExists(sqlU, sqlUc, cID):
            print("Please enter the new permission level, must be between 1-3")
            print("1:Student - 2:Teacher - 3:Admin")
            level = raw_input()
            if (level == "1") or (level == "2") or (level == "3"):
                sqlUc.execute("""UPDATE "main"."User" SET "PermissionLevel" = ? WHERE  "UserID" = ?""",(int(level), int(cID), ))
                sqlU.commit()
                print("Operation was successful")
            else:
                print("Error, value must be between 1 and 3")
                wait()
        else:
            print("Unknown user ID...")
            wait()

#-------------------------------------------END OF CONSOLE CLASS-------------------------------------------
#-------------------------------------------END OF CONSOLE CLASS-------------------------------------------
#-------------------------------------------END OF CONSOLE CLASS-------------------------------------------

class sender(threading.Thread):

    def __init__(self, sendlist, data, port = 50008, timeout = 0.3):
        super(sender, self).__init__()
        self.sendlist = sendlist
        self.data = data
        self.dport = port
        self.timeout = timeout

    def run(self):
        for client in range(0, len(self.sendlist)): #For each client in the provided list, try to send the command
            try:
                self.send(self.sendlist[client], self.data)
            except:

                info("Command to "+ str(self.sendlist[client])+ " failed, commmand was " + str(self.data)) #If a message to client times out

    def send(self, client, data):
        debug("sending " + str(client) + " " + str(data))
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)
        debug("Connecting to client at " +str(client) + " " + str(self.dport))
        s.connect((client, self.dport))
        s.sendall(json.dumps((data,)))
        s.close()
        debug("Data is sent!")

#-------------------------------------------END OF SENDER CLASS-------------------------------------------

class ping(threading.Thread):

    def __init__(self):
        super(ping, self).__init__()
        self.pingFreq = 3

    def run(self):
        sql = sqlite3.connect('Pi-control.db')
        while True:
            self.pinger2(sql)
            sleep(self.pingFreq) #Wait for 3 seconds before pinging again

    def pinger2(self,sql):
        sqlp = sql.cursor()
        for row in sqlp.execute("""SELECT IP FROM ClientID"""): #for every client
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(0.3)
            try:
                s.connect((row[0], 50008))    #Try to connect
                s.sendall(json.dumps(('Ping',)))
                self.data = s.recv(1024)
                s.close()
            except error: #If it fails, delete them
                sqlp.execute("""DELETE FROM ClientID WHERE IP = ?""", row)
                sql.commit()

#-------------------------------------------END OF PINGER CLASS-------------------------------------------

class transmissionHandler(threading.Thread):
    def __init__(self, ip, data):
        super(transmissionHandler, self).__init__()
        debug(ip)
        self.ip = ip
        self.data = data

    def run(self):
        sql = sqlite3.connect('Pi-control.db') #Connect to database
        self.Handler(self.ip, self.data, sql) #Call main handler

    def Handler(self, ip, data, sql): #Main handler, will have more functionality later
        info("Handler called!!")
        level = checkToken(self.data[2])
        self.interpreter(ip, data, level, sql) #Calls main interpreter that is on the second thread

    def interpreter(self, ip, data, level, sql):
        debug(data)
        if data[0] == "Server": #If the incoming command is aimed at the server
            if (data[1][0] == "name") and (level >1):
                for i in range(0, len(data[3])):
                    self.name = (data[1][1])
                    self.ip = (data[3][i])
                    print("IP is " + str(self.ip) + " Name is " + str(self.name))
                    sqld = sql.cursor()
                    debug(self.ip)
                    sqld.execute("""SELECT Serial FROM ClientID WHERE Ip = ? """,(self.ip,) )
                    d = (self.name, sqld.fetchone()[0])
                    sqld.execute("""UPDATE Metadata SET Name = ? WHERE Serial = ?""",d)
                sql.commit()
                sql.close()
            elif (data[1][0] == "Password"):
                self.password = data[1][1]
                #self.ip =
                debug("new password is " + data[1][1])
                sqld = sql.cursor()
                sqld.execute("""SELECT UserID FROM User WHERE Token  = ? """,(data[2],))
                ID = sqld.fetchone()
                hashresult = createHash(self.password)
                sqld.execute("""UPDATE "main"."User" SET "Salt" = ?, "Hash" = ? WHERE  "Token" = ?""",(str(hashresult[0]), str(hashresult[1]), data[2]))
                sql.commit()
                sql.close()
        elif (data[0] == "Relay"): #If the incoming command is due to be relayed on to the client
            debug("Relay data arrived!") #Relay will later be only way to communicate with pi
            debug(data)
            if data[1][1] == []:
                s = sender(data[3], (data[1]))
                s.run()
            else:
                s = sender(data[3], (data[1]))
                s.run()
        elif (data[0] == "FeatureList"):
                MenuMake = clientMenu(self.ip, checkToken(data[2]))
                MenuMake.run()

#Server communications - ("Server", (Message, (Payload)), Token, (Recipients)



#-------------------------------------------END OF transmissionHandler CLASS-------------------------------------------


#*******************************************START OF MAIN PROGRAM*******************************************
#*******************************************START OF MAIN PROGRAM*******************************************
#*******************************************START OF MAIN PROGRAM*******************************************

def wait():
    print("")
    raw_input("Press any key to continue..")
    print("")

def listit(t):
    if isinstance(t, (list, tuple)):
        return list(map(listit, t))
    else:
        return t


def randomDigits(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    toreturn = random.randint(lower, upper) #Generates a random number for the hash
    info("Hash generated is " + str(toreturn))
    return toreturn


def createHash(password):
    salt = randomDigits(32) #Generates random number for salt
    debug("The salt is "+ str(salt))
    hashResult = hashlib.sha512(str(salt) + str(password)).hexdigest() #Generates sha512 hash
    return (salt, hashResult)


def decodeHash(hash, salt, password): #Takes hash and salt from database and the provided password, generated a hash from the salt and password and checks if they are equal
    info("At hash, hash is " + str(hash) + " and password is " + str(password))
    hashResult = hashlib.sha512(str(salt) + str(password)).hexdigest()
    info("Hash in database is " + str(hashResult) + " While hash provided is " + str(hash))
    if hashResult == hash:
        return True
    else:
        return False


def getToken(credentials, sql, sqlc):
    username = (credentials[0],)
    sqlc.execute("""SELECT UserID, Username, Salt, Hash, PermissionLevel, Token, NoToken FROM User WHERE Username = ? """, username)
    fetch = sqlc.fetchone()
    debug(str(fetch))   #Checks if user exits
    if not (fetch == None):
        sqlc.execute("""SELECT Hash, Salt FROM User WHERE Username = ? """, username)
        hashSalt = sqlc.fetchone()
        debug(str(fetch[6]))
        if (decodeHash(hashSalt[0], hashSalt[1], credentials[1])) == True:
            if str(fetch[6]) == "1":
                return username[0] # If the user is set up to disable the use of tokens
            else:
                return randomDigits(10) #If set up to use tokens, username was correct and password was correct
        else:
            return False #Username correct, password not
    else:
        return False #Username unknown


def checkToken(token):
    sqls = sqlite3.connect('Pi-control.db')
    sqld = sqls.cursor()
    token = (token, )
    sqld.execute("""SELECT PermissionLevel FROM User WHERE Token = ? """, token)
    result = sqld.fetchone()
    if not (result == None): #If result = anything other than none, then that token exits
        debug(str(result))
        return result[0] #Return the username
    else:
        return 0




def getPermission(user): #Future implementation
    pass

def checkPermission(ID, Required): #Future implementation
    pass

def datachecker2(sql, sqlc): #Main overarching main thread communication interpreter
    info('')
    info('Waiting for incoming messages')
    s.settimeout(10) #Time to wait before going onto next function
    try:
        client, address = s.accept()
        sleep(0.1)
        data = client.recv(size)
        if data:
            data = json.loads(data) #Convert data from a json object to a list
            if (data[0] == 'Register'): #If data is register, the command for setting up a new pi
                debug(data)
                ip = (address[0],)
                sqlc.execute("""SELECT CId, IP, Serial FROM ClientID WHERE IP = ? """, ip) #Checks if pi is already in the database (avoids duplicates)
                if sqlc.fetchone() == None:
                    serial = str(data[1])
                    dat = (address[0], serial)
                    sqlc.execute("""INSERT INTO ClientID VALUES(NULL,?, ?)""", dat) #Adds client
                    sqlc.execute("""SELECT Serial FROM Metadata WHERE Serial = ? """, (serial,))
                    if sqlc.fetchone() == None:
                        sqlc.execute("""INSERT INTO Metadata VALUES(?,NULL) """, (serial,)) #If we have never met pi before, save its serial number
                    sql.commit()
                    info('')
                    info('-------------------------------------')
                    info('Client at ' + str(address[0]) +' added to list')
                    info('-------------------------------------')
                    info('')
                client.send(json.dumps(('Accept',))) #Alert the pi that it has been added
                sleep(0.05)

            elif data[0] == "Token": #Request for token from the client
                credentials = data[1]
                ip = (address[0],)
                result = getToken(credentials, sql, sqlc) #Create token
                if not (result == False):
                    d = (result, credentials[0])
                    debug(str(d))
                    sqlc.execute("""UPDATE "main"."User" SET "Token" = ? WHERE  "Username" = ?""", d)
                    sql.commit()
                    #sqlc.execute("""UPDATE User SET Token = ? WHERE Username = ?""",d)
                else:
                    result = 0
                client.send(json.dumps((result,)))

            else: #If not either of the above, check if requestlist
                debug(data)
                debug("Data it cant get is" + str(data[2]))
                if (checkToken(data[2]) > 0): #Checks level
                    if data[0] == 'RequestList':
                        sqlc.execute("""SELECT ClientID.IP, ClientID.Serial, Metadata.Name
                                    FROM ClientID
                                    INNER JOIN Metadata
                                    ON ClientID.Serial = Metadata.Serial""") #Pulls data from 2 tables to build the list of clients
                        tosendlist = sqlc.fetchall()
                        cm = clientMenu(address[0], checkToken(data[2]), "Home", tosendlist) #Passes this information to a new thread to build menu
                        cm.run()


                        #client.send(json.dumps((tosendlist,)))
                    else:
                        t = transmissionHandler(address[0], data) #If none of the above, switch to a new thread to allow main thread to continue
                        t.daemon = True
                        t.start()

                    client.close()
                else:
                    warning("Invalid login")
    except timeout:
        pass


def createDatabase(sqlc, sql):
    info("Creating database")
    sqlc.execute('''CREATE TABLE ClientID
(
CId INTEGER PRIMARY KEY AUTOINCREMENT,
IP varchar(15) NOT NULL,
Serial varchar(4) NOT NULL
)''')
    sqlc.execute("""CREATE  TABLE IF NOT EXISTS "main"."Connection" ("UserID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "IP" VARCHAR NOT NULL , "Key" INTEGER)""")
    sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."Metadata" ("Serial" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE , "Name" VARCHAR)""")
    #sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."Group" ("GroupID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Name" VARCHAR NOT NULL , "Description" VARCHAR)""")                 #To be added later
    #sqlc.execute("""CREATE  TABLE  IF NOT EXISTS "main"."GroupConnection" ("ID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Serial" VARCHAR NOT NULL , "GroupID" INTEGER NOT NULL )""")    #To be added later
    sqlc.execute("""CREATE TABLE IF NOT EXISTS "User" ("UserID" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "Username" VARCHAR NOT NULL , "Salt" VARCHAR NOT NULL , "Hash" VARCHAR NOT NULL , "PermissionLevel" INTEGER NOT NULL, "Token" VARCHAR , "NoToken" BOOL DEFAULT FALSE)""")
    #sql.commit()

def setupNetworking(): #Create an inital network object, s
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
        info("No database found, creating one")
    try:
        sqlc.execute("""DROP TABLE "main"."Connection" """)
    except:
        pass
    createDatabase(sql, sqlc)
    return sqlc

def consoleMessage():
        print("\n" * 5)
        print("")
        print("---------------------")
        print("Server is running")
        print("---------------------")
        print("")
        print("To access control console press c and then enter")
        print("------------------------------------------------")

#**********************************************************- Main program - **********************************************************


mainLoop = True
while mainLoop:
    try:

        size = 1024
        s = setupNetworking() #Create network object
        clientlist = []
        sql = sqlite3.connect('Pi-control.db') #Connect to database
        sqlc = InitalSQL(sql) #Create SQL curser

        p = ping()
        p.daemon = True
        p.start() #Starts the pinger thread

        c = console()
        c.daemon = True
        c.start() #Starts the console thread

        #consoleMessage()

        b = broadcaster()
        b.daemon = True
        b.start() #Starts the broadcasting thread

        while 1:
            datachecker2(sql,sqlc)



    except:
        print('************************************')
        print("System error...")
        traceback.print_exc(file=sys.stdout) #Prints out traceback error
        print('************************************')
        print("")
        break

