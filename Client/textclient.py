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
    root = Tkinter.Tk()
    root.withdraw()
    file_path = tkFileDialog.askopenfilename()
    return file_path


def ftpDrop(serverIP):
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    filename = submitFile()
    file = open("ftper", "w")
    #print("about to write")
    file.write("""#!/bin/bash
ftp -n -i $1 <<EOF
user anonymous " "
binary
cd handin
put $2 $3
EOF""")
    file.close()
    #print("about to call")
    #print(filename)
    #print(serverIP)
    #print(os.path.basename(filename))
    thing = call(["sh", "ftper", serverIP, filename, os.path.basename(filename)])
    print(thing)
    print(thing)
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
            s.send(json.dumps((message, "", mainToken)))
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
                    #print('data is ' + str(data))
                    data = json.loads(data)
                    conn.close()
                    s.close()
                    gotdata = True
                    waiting = False
                    #print(data)

                    return data[0]
                else:
                    warning('waiting for data..')
                    sleep(0.2)
        except socket.error:
            warning('Can not find server, trying again')
            sleep(2)
            traceback.print_exc(file=sys.stdout)

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
        s.send(json.dumps(message))
    else:
        s.send(json.dumps((message, payload, mainToken)))
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



def grouper(ip):
    MenuRun = True
    while MenuRun == True:
        print('What would you like to do?')
        print('')
        break


class LoginC():
    def __init__(self, serverIP):
        self.serverIP = serverIP
        self.token = ""

    def getToken(self):
        success = False
        while success == False:
            credentials =  self.details()
            self.token = transmiterReturn("Token", self.serverIP, credentials, 50000)
            if (int(self.token) == 0):
                print("\n"*10)
                print("---------------------")
                print("Incorrect credentials")
                print("---------------------")
                print("")
            else:
                success = True
        debug("Token is " + str(self.token))
        global mainToken
        mainToken = self.token



    def details(self):
        print("Please enter your username")
        username = (raw_input()).lower()
        print("Please enter password")
        password = getpass.getpass()
        debug(password)
        return ((username, password))





def ipmenu(ip, serverIP):
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
    transmiter(MenuName, serverIP, None, 50000)
    menuList = (transmiterListen(50010))
    #print("Menulist is "+ str(menuList))
    menurun = True
    if menuList == []:
        print("You have no permissions for this client")
        sleep(3)
    while menurun == True:
        print('What would you like to do with this Raspberry Pi?')
        print('Currently connected to ' + str(piIp))
        print('')
        for count in range(1, len(menuList)+1):
            print(str(count) + ". " + str(menuList[count-1][1]))
        answer = raw_input()
        try:
            answer = int(answer)
        except:
            print("Invalid value supplied")
            sleep(2)
            continue


        menurun = menuInterpreter(menuList, answer, piIp, serverIP)
        #Interpreter
def menuInterpreter(menuList, answer, piIp, serverIP):
        global allClients
        if answer in range(1, len(menuList)+1):
            requested = answer -1

            #----------------------Custom Functions-------------------

            if menuList[requested][2] == "Exit":
                return False
            if menuList[requested][2] == "Refresh":
                return False
            if menuList[requested][2] == "ClientMenu":
                clientMenu(menuList[requested][1],serverIP)
                return False
            if menuList[requested][4] == "GetFile":
                print("submit file")
                ftpDrop(serverIP)

            #----------------------Custom Functions End---------------

            if (not (menuList[requested][3] == False)):
                print(menuList[requested][3])
                secondResponse = raw_input()
            else:
                secondResponse = ""
            if (menuList[requested][2][0] == "all"):
                allC = True
                menuList[requested][2] = menuList[requested][2][1]
            else:
                allC = False

            if (menuList[requested][2] == "pi") or (menuList[requested][2] == "server"):
                tosend = ["", ["", []], mainToken, []]
                if (menuList[requested][2] == "pi"):
                    tosend[0] = "Relay"
                    if allC:
                        tosend[3] = allClients
                    else:
                        tosend[3] = [piIp, ]
                    tosend[1][0] = menuList[requested][4]
                    pass
                    transmiter(tosend, serverIP, None, 50000, True)

                elif (menuList[requested][2] == "server"):
                    message = ((secondResponse, piIp))
                    if allC:
                        message = ((secondResponse, allClients))
                    else:
                        message = ((secondResponse, piIp))
                    transmit = False
                    transmiter(menuList[requested][4], serverIP, message,  50000)
                else:
                    pass


                return False


def menu(clientlist, ipaddress):
    global allClients
    while True:
        clientlist = grablist(ipaddress)
        clearer()
        lineMaker(3)
        print('Raspberry Pi Classroom Management Text Client')
        print('----------------------------------------')
        print('')
        clientlist = clientlist[1]
        clientIPs = clientlist[1]


        menuOption = clientlist[0]


        for clientnum in range(0, len(menuOption)):
            print(str(clientnum + 1) + ". " + menuOption[clientnum][1])
        print("")
        print('Connected Raspberry Pis')
        print('-----------------------')


        for clientnum in range(0, len(clientIPs)):
            print(str(clientnum + len(menuOption) + 1) + ". " + clientIPs[clientnum][1][0] + " - " + clientIPs[clientnum][1][1])
            clientIPs[clientnum][1] = clientIPs[clientnum][1][0]
        allClients = []
        for i in range(0, len(clientIPs)):
            allClients.append(clientIPs[i][1])

        answer = raw_input()

        fullMenu = menuOption + clientIPs
        try:
            answer = int(answer)
        except:
            continue
        menuInterpreter(fullMenu, answer, 0, ipaddress)




startupimage2()
ipaddress = broadcastfinder()
login = LoginC(ipaddress)
login.getToken()
#print('Attempting to connect to server')
clientlist = grablist(ipaddress)
menu(clientlist, ipaddress)
