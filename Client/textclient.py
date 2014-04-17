#!/usr/bin/python
import os, socket, json, getpass
from time import sleep
import traceback
import sys
from logging import debug, info, warning, basicConfig, INFO, DEBUG, WARNING
import Tkinter, tkFileDialog
from subprocess import call


basicConfig(level=WARNING)

ServerIP = ""


def clearer():
    #Simple function that clears the screen
    os.system('cls' if os.name=='nt' else 'clear')

mainToken = 0
allClients = []

def startupimage2():
    clearer()
    #Everyone loves awesome ASCII art!
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
    global ServerIP
    print('Searching for server....')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 50011))
    data, wherefrom = s.recvfrom(1500, 0)
    #print (data + " " + repr(wherefrom[0]))
    ServerIP = wherefrom[0]
    return(wherefrom[0])

def lineMaker(lines):
    for i in range(0, lines):
        print("")


def submitFile():
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




def askForFile():
    pass
    #Tk().withdraw()
    #filename = askopenfilename()
    #return filename


def grablist(ipaddress): #Job is to grab the list off the server of connected clients
    global mainToken
    gotdata = False
    while gotdata == False: #Will loop till it gets reply from the server
        try:
            message = 'RequestList'
            host = ipaddress
            port = 50000
            size = 1024
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((host,port))
            s.send(json.dumps((message, "", mainToken))) #Sends request plus token
            waiting = True
            s.close()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sleep(0.005)
            s.bind(('', 50009))
            s.listen(2)
            conn, addr = s.accept()
            while waiting == True:
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
        except socket.error:
            warning('Can not find server, trying again')
            sleep(2)
            debug(traceback.print_exc(file=sys.stdout)) #If server is unavilable give a traceback

def transmiter(message, ip, payload = None, port = 50008, raw = False):
    global mainToken
    #port = 50008
    #print('---------')
    #print(message)
    #print(ip)
    #print('---------')
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print((ip,port))
    s.connect((ip,port))
    #print("Sending")
    #print((json.dumps((message, payload))))
    if raw:
        debug(message)
        s.send(json.dumps(message)) #If it is raw ready to go list
    else:
        s.send(json.dumps((message, payload, mainToken))) #If normal message format
    sleep(0.05)
    s.close()


def transmiterReturn(message, ip, payload = None, port = 50008):
    global mainToken
    #port = 50008
    #print('---------')
    #print(message)
    #print(ip)
    #print('---------')
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print((ip,port))
    s.connect((ip,port))
    #print("Sending")
    #print((json.dumps((message, payload))))
    s.send(json.dumps((message, payload, mainToken)))
    debug(json.dumps((message, payload, mainToken)))
    data = s.recv(size)
    if data:
        #print('data is ' + str(data))
        data = json.loads(data)
        s.close()
        gotdata = True
        waiting = False
        return data[0]
    else:
        warning('waiting for data..')
        sleep(0.2)

def transmiterListen(port):
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
    #print("The data is " + str(data))
    #print(data[0][1])
    return data[0][1]



def grouper(ip): #Not currently implemented
    MenuRun = True
    while MenuRun == True:
        print('What would you like to do?')
        print('')
        break


class LoginC(): #The main login system for managing logins and tokens
    def __init__(self, serverIP):
        self.serverIP = serverIP
        self.token = ""

    def getToken(self):
        success = False
        while success == False: #Keep repeating till they get successful credentials
            credentials =  self.details()
            self.token = transmiterReturn("Token", self.serverIP, credentials, 50000) #Checks credentials
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
        print("Please enter your username")
        username = (raw_input()).lower()
        print("Please enter password")
        password = getpass.getpass() #Uses getpass to hide password
        debug(password)
        return ((username, password))





def ipmenu(ip, serverIP): #NO LONGER USED - Kept for old reference
    clearer()
    menurun = True
    while menurun == True:
        print('What would you like to do with this Raspberry Pi?')
        print('Currently connected to ' + str(ip[0]))
        print('')
        print('1. Reboot')
        print('2. Shutdown')
        print('3. Connect via Scratch GPIO')
        print('4. Assign a name')
        print('5. Flash LEDs on robot')
        print('6. Alive check')
        print('7. Disable all GPIO')
        #print('8. Enable camera live video to this IP - NOT WORKING YET')
        print('9. Add to group')
        print('10. Return to main menu')


        answer = raw_input()
        transmit = True
        menurun = False
        if answer == '1':
            message = 'Reboot'
        elif answer == '2':
            message = 'Shutdown'
        elif answer == '3':
            message = 'Scratch'
        elif answer == '4':
            print('Please enter name')
            name = raw_input()
            message = ((name, ip[0]))
            transmit = False
            transmiter('name', serverIP, message,  50000)

        elif answer == '5':
            message = 'LED'
        elif answer == '6':
            message = 'Ping'
        elif answer == '7':
            message = 'GPIOoff'
        elif answer == '8':
            message = 'CameraFeed'
        elif answer == '9':
            transmit = False
            grouper(ip)
        elif answer == '10':
            transmit = False
            #menu()
        else:
            print('Please enter valid option')
            sleep(1)
            menurun = True
            transmit = False

        if transmit == True:
            print('Transmitting message')
            #sleep(1)
            #print("The server IP is " + str(ip))
            transmiter(message, ip)
            
# Server relay communications - (Relay, (Message, (Payload)), Token, (Recipients)


def clientMenu(ip, serverIP, MenuName = "FeatureList"):
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
        #Interpreter
def menuInterpreter(menuList, answer, piIp, serverIP):
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

startupimage2()
ipaddress = broadcastfinder()
login = LoginC(ipaddress)
login.getToken()
clientlist = grablist(ipaddress)
menu(clientlist, ipaddress)
