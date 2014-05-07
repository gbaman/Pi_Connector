#!/usr/bin/python
import os, socket, json, getpass
from time import sleep
import traceback
import sys
from logging import debug, info, warning, basicConfig, INFO, DEBUG, WARNING
import Tkinter, tkFileDialog
from subprocess import call
try:
    from Crypto.PublicKey import RSA
    from Crypto import Random
    import base64
    crypt = True
except:
    print("Error!!! PyCrypto library is not installed")
    print("Encryption on network communications has been disabled")
    crypt = False

#------------------Global variables and constants-----------------
basicConfig(level=WARNING)       #Set the debug level, options include DEBUG, INFO and WARNING
ServerIP = ""
mainToken = 0
allClients = []
#--------------END Global variables and constants END-------------


def clearer():
    """Simple function that clears the screen.
    It works by checking if the OS is windows based, if it is run cls, if not run clear (linux/unix command)"""
    os.system('cls' if os.name=='nt' else 'clear')


def startupimage2():
    """Displays ASCII startup art. Everyone loves awesome ASCII art!"""
    clearer()
    print('''

  _____           _____ _
 |  __ \         |  __ (_)         .~~.   .~~.
 | |__) |__ _ ___| |__) |         '. \ ' ' / .'
 |  _  // _` / __|  ___/ |         .~ .~~~..~.
 | | \ \ (_| \__ \ |   | |        : .~.'~'.~. :
 |_|  \_\__,_|___/_|   |_|       ~ (   ) (   ) ~
                                ( : '~'.~.'~' : )
                                 ~ .~ (   ) ~. ~
                                  (  : '~' :  )
                                   '~ .~~~. ~'
   _____            _             _ _  '~'
  / ____|          | |           | | |
 | |     ___  _ __ | |_ _ __ ___ | | | ___ _ __
 | |    / _ \| '_ \| __| '__/ _ \| | |/ _ | '__|
 | |___| (_) | | | | |_| | | (_) | | |  __| |
  \_____\___/|_| |_|\__|_|  \___/|_|_|\___|_|

    ''')
    sleep(2)
    

    
def broadcastfinder():
    """Uses UDP network sockets to locate a network broadcast server"""
    global ServerIP
    print('Searching for server....')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 50011))
    data, wherefrom = s.recvfrom(1500, 0)
    ServerIP = wherefrom[0]
    return(wherefrom[0])

def lineMaker(lines):
    """
    :param lines: Number of blank lines to be generated

    Creates blank lines on the commandline

    """
    for i in range(0, lines):
        print("")


def submitFile():
    """
    :return: The path of the selected file. Returns False if there is an error

    SubmitFile attempts to open a TK window to allow the user to select a file"""
    try:
        os.chdir(os.path.expanduser("~")) #Changes to home directory
        root = Tkinter.Tk()
        root.withdraw()
        file_path = tkFileDialog.askopenfilename() #Creates a TK file selection window
        return file_path
    except:
        print("Error, unable to open file selection window")
        sleep(3)
        return(False)


def ftpDrop(serverIP):
    """
    :param serverIP: IP address of the connected server

    Creates a script to upload a selected file to an FTP server.
    It calls submitFile() which lets the user to select a file to be uploaded.
    It then creates a BASH script called ftper and runs the BASH script, passing it the file path
    """
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    filename = submitFile()
    if not (filename == False):
        file = open("ftper", "w") #Create a bash script file to upload to server
    #print("about to write")
        file.write("""#!/bin/bash
ftp -n -i $1 <<EOF
user anonymous " "
binary
cd handin
put $2 $3
EOF""")
        file.close()
        thing = call(["sh", "ftper", serverIP, filename, os.path.basename(filename)]) #Runs bash script
    #print("called")
        call(["rm", "ftper"])

def grablist(ipaddress): #Job is to grab the list off the server of connected clients
    """
    :param ipaddress: The IP address of the server you are requesting the list from

    Job is to grab the list off the server of connected clients
    It does this by making a connection to the server and sending a request, the message is "RequestList"
    It then waits for a response on a different port. When it recieves its data, it closes the connection.
    It then loads with data with json.load to convert to a list of lists and returns a list of menu options
    """
    global mainToken
    gotdata = False
    while gotdata == False: #Will loop till it gets reply from the server
        try:
            message = 'RequestList'
            host = ipaddress
            port = 50000 #Request made using port 5000
            size = 1024
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((host,port))
            s.send(json.dumps((message, "", mainToken))) #Sends request plus token
            waiting = True
            s.close()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sleep(0.005)
            s.bind(('', 50009)) #Request is replied on port 50009
            s.listen(2)
            conn, addr = s.accept()
            while waiting == True: #While it waits for data to arrive
                data = conn.recv(1024)
                if data:
                    data = json.loads(data)
                    conn.close()
                    s.close()
                    gotdata = True
                    waiting = False

                    return data[0]
                else:
                    warning('waiting for data..')
                    sleep(0.2)
        except socket.error: #If there is a socket timeout. Normally happens when server dies
            warning('Can not find server, trying again')
            sleep(2)
            debug(traceback.print_exc(file=sys.stdout)) #If server is unavilable give a traceback

def transmiter(message, ip, payload = None, port = 50008, raw = False):
    """

    :param message: Message to be sent, this is normally a list of lists
    :param ip: IP address to send to
    :param payload: By default, no payload is included, if for additional information
    :param port: Port to send on
    :param raw: If raw is true, only the message is used, this allows entire list to be generated in the program
    :return: None

    Transmitter opens network sockets and sets information passed to it. It supports 2 modes, standard and raw
    If raw mode is enabled, it sends the provided list, maintaining its formatting.
    """
    global mainToken
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip,port))
    if raw:
        debug(message)
        s.send(json.dumps(message)) #If it is raw ready to go list
    else:
        s.send(json.dumps((message, payload, mainToken))) #If normal message format
    sleep(0.05)
    s.close()


def transmiterReturn(message, ip, payload = None, port = 50008, raw = False, allData = False):
    """

    :param message: Message to be sent, this is normally a list of lists
    :param ip: IP address to send to
    :param payload: By default, no payload is included, if for additional information
    :param port: Port to send on
    :param raw: If raw is true, only the message is used, this allows entire list to be generated in the program
    :return: Data recieved

    Majority of same code as transmitter, except also includes a wait for return data on the socket
    """
    global mainToken
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip,port))
    if raw:
        s.send(json.dumps(message))
    else:
        s.send(json.dumps((message, payload, mainToken)))
    debug(json.dumps((message, payload, mainToken)))
    data = s.recv(size)
    if data:
        debug(data)
        data = json.loads(data)
        s.close()
        gotdata = True
        waiting = False
        if allData:
            return data
        else:
            return data[0]
    else:
        warning('waiting for data..')
        sleep(0.2)

def transmiterListen(port):
    """

    :param port: Port to listen on for communications
    :return: Data recieved

    Just binds to a port and waits for communications to come in
    """
    global mainToken
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    info("Socket bound!")
    s.listen(5)
    conn, addr = s.accept()
    debug(addr)
    data = conn.recv(1024)
    conn.close()
    s.close()
    data = json.loads(data)
    return data[0][1]

class LoginC():
    """
    The main login system for managing logins and tokens
    """
    def __init__(self, serverIP):
        """

        :param serverIP: The IP address of the server
        :return: None

        """
        self.serverIP = serverIP
        self.token = ""
        self.publicKey = ""

    def getPublicKey(self):
        publicKey = transmiterReturn("PrivateKey", self.serverIP, None, 50000, False, True)
        #publicKey = json.loads(publicKey)
        debug("Public key is " + str(publicKey[1]))
        if publicKey == "False":
            publicKey = False
            self.publicKey = publicKey
        else:
            self.publicKey = publicKey[1]


    def getToken(self):
        """
        Requests a token from the server then stores it in global variable mainToken
        """
        global crypt
        global mainToken
        self.getPublicKey()
        success = False
        while success == False: #Keep repeating till they get successful credentials
            credentials =  self.details()
            if (self.publicKey == "False") or (crypt == False):
                warning("Warning, encryption disabled")
                self.token = transmiterReturn("Token", self.serverIP, credentials, 50000) #Checks credentials
            else:
                debug("Importing this key " + str(self.publicKey))
                mainKey = RSA.importKey(self.publicKey)
                encryptedData = base64.b64encode((mainKey.encrypt(json.dumps(credentials), 32))[0])
                tosend = ("Encrypted",("Token", encryptedData, mainToken))
                debug(tosend)
                self.token = transmiterReturn(tosend, self.serverIP, None, 50000, True) #Checks credentials

            if ((str(self.token)) == "0"):
                print("\n"*10)
                print("---------------------")
                print("Incorrect credentials")
                print("---------------------")
                print("")
            else:
                success = True
        debug("Token is " + str(self.token))
        global mainToken #Sets the main communication token
        mainToken = self.token



    def details(self):
        """
        :return: Login details (username, password)

        Gets the username and password from the user
        """
        print("Please enter your username")
        username = (raw_input()).lower()
        print("Please enter password")
        password = getpass.getpass() #Uses getpass to hide password
        debug(password)
        return ((username, password))


def clientMenu(ip, serverIP, MenuName = "FeatureList"):
    """

    :param ip: IP address of Raspberry Pi
    :param serverIP: IP address of the server
    :param MenuName: The menu type, default being FeatureList
    :return: None

    The main Raspberry Pi menu drawer. It requests the menu, then iterates through the provided menu displaying it all
    """
    global mainToken
    lineMaker(3)
    debug(login.token)
    #print("IP is "+str(ip))
    piIp = ip
    transmiter(MenuName, serverIP, None, 50000) #Request a client menu
    menuList = (transmiterListen(50010)) #The menu object
    #print("Menulist is "+ str(menuList))
    menurun = True
    if menuList == []: #If they have no permissions for that client, should never occure
        print("You have no permissions for this client")
        sleep(3)
    while menurun == True:
        print('What would you like to do with this Raspberry Pi?')
        print('Currently connected to ' + str(piIp))
        print('')
        for count in range(1, len(menuList)+1): #Goes through the list displaying the menu
            print(str(count) + ". " + str(menuList[count-1][1]))
        answer = raw_input()
        try:
            answer = int(answer) #Checks if the entered value can be converted to an integer
        except:
            print("Invalid value supplied")
            sleep(2)
            continue


        menurun = menuInterpreter(menuList, answer, piIp, serverIP) #Runs the main menu interpreter


def menuInterpreter(menuList, answer, piIp, serverIP):
    """

    :param menuList: The dynamically generated menu, generated by the server, in list form
    :param answer: The option selected by the user
    :param piIp: IP address of the Raspberry Pi
    :param serverIP: IP address of the server
    :return: False

    The main interpreter for the menu system. It takes values provided by the user selecting an item in menu or clientMenu.
    It then interprets the values in the list provided, running through a number of if statements.
    """
    global allClients
    if answer in range(1, len(menuList)+1):
        requested = answer -1

        #----------------------Custom Functions-------------------

        if menuList[requested][2] == "Exit": #Returns to previous menu
            return False
        if menuList[requested][2] == "Refresh":
            return False
        if menuList[requested][2] == "ClientMenu":
            clientMenu(menuList[requested][1],serverIP)
            return False
        if menuList[requested][4] == "GetFile":
            #print("submit file")
            ftpDrop(serverIP) #FTP system
        if menuList[requested][2] == "ExitAll":
            sys.exit() #Quits python program

        #----------------------Custom Functions End---------------

        if (not (menuList[requested][3] == False)):
            print(menuList[requested][3])
            secondResponse = raw_input() #If the option requires additional information
        else:
            secondResponse = "" #If it does not, leave field blank
        if (menuList[requested][2][0] == "all"): #Should I send it to all clients?
            allC = True
            menuList[requested][2] = menuList[requested][2][1] #Reverts it back to normal pi mode for legacy interpreter
        else:
            allC = False

        if (menuList[requested][2] == "pi") or (menuList[requested][2] == "server"): #Checks that it isnt a direct IP address or other
            tosend = ["", ["", ["",]], mainToken, []] #Builds unfilled in response
            #tosend key --- [server or relay, [command, [payload,]], token, [clients],]
            if (menuList[requested][2] == "pi"): #If is meant to be sent to a Raspberry Pi
                tosend[0] = "Relay" #Sets it as relay as all communications should relay via the server to the client, no direct communications!
                if allC:
                    tosend[3] = allClients #If it is to be sent to all clients, put all clients into the list
                else:
                    tosend[3] = [piIp, ] #If not, just send to a single IP address
                tosend[1][0] = menuList[requested][4] #Because being relayed, tosend[0] will = relay, tosend[1][0] is the command for the actual client
                tosend[1][1][0] = secondResponse #Add the second response to the payload
                transmiter(tosend, serverIP, None, 50000, True) #Send it!

            elif (menuList[requested][2] == "server"): #If it is meant to be only sent to server (change password for example)
                tosend[0] = "Server" #Destination
                tosend[1][0] = menuList[requested][4] #Command
                tosend[1][1] = secondResponse #Adds second reponse to the payload
                if allC:
                    tosend[3] = allClients #If it is to be sent to all clients, put all clients into the list
                else:
                    tosend[3] = [piIp, ] #If not, just send to a single IP address
                transmiter(tosend, serverIP, None,  50000, True) #Send it!
            else:
                pass
            return False
    else:
        print("Invalid option")
        sleep(2)



def menu(clientlist, ipaddress):
    """

    :param clientlist: List of client information
    :param ipaddress: IP address of the server
    :return: None

    The main home menu system. It takes the dynamically generated list from the server, iterates through it and
    displays the options. It then displays all the IP addresses of clients connected to the server
    """
    global allClients
    while True:
        clientlist = grablist(ipaddress) #Gets the list of clients via legacy method, TO UPGRADE LATER
        clearer()
        lineMaker(3)
        print('Raspberry Pi Classroom Management Text Client')
        print('----------------------------------------')
        print('')
        clientlist = clientlist[1]
        clientIPs = clientlist[1]
        menuOption = clientlist[0] #Split the menu
        for clientnum in range(0, len(menuOption)): #Iterations through prebuilt menu
            print(str(clientnum + 1) + ". " + menuOption[clientnum][1])
        print("")
        print('Connected Raspberry Pis')
        print('-----------------------')


        for clientnum in range(0, len(clientIPs)):
            print(str(clientnum + len(menuOption) + 1) + ". " + clientIPs[clientnum][1][0] + " - " + clientIPs[clientnum][1][1]) #Print the pis
            clientIPs[clientnum][1] = clientIPs[clientnum][1][0]
        allClients = []
        for i in range(0, len(clientIPs)):
            allClients.append(clientIPs[i][1])

        answer = raw_input()

        fullMenu = menuOption + clientIPs #The full length
        try:
            answer = int(answer) #Tries to convert to integer
        except:
            continue #If isnt integer, loop again
        menuInterpreter(fullMenu, answer, 0, ipaddress)


#----------------------------------------------------------------Main program-----------------------------------------------------------------

if __name__ == '__main__':
    startupimage2()
    ipaddress = broadcastfinder()
    login = LoginC(ipaddress)
    login.getToken()
    clientlist = grablist(ipaddress)
    menu(clientlist, ipaddress)
