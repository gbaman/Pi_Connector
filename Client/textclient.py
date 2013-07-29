import os, socket, json
from time import sleep

def clearer():
    #Simple function that clears the screen
    os.system('cls' if os.name=='nt' else 'clear')


def startupimage2():
    clearer()
    #Everyone loves awesome ASCII art!
    print('''

   _____ _          _                       
  / ____| |        (_)                          .~~.   .~~.
 | (___ | |__  _ __ _ _ __ ___  _ __  _   _    '. \ ' ' / .'
  \___ \| '_ \| '__| | '_ ` _ \| '_ \| | | |    .~ .~~~..~. 
  ____) | | | | |  | | | | | | | |_) | |_| |   : .~.'~'.~. :
 |_____/|_| |_|_|  |_|_| |_| |_| .__/ \__, |  ~ (   ) (   ) ~ 
                               | |     __/ | ( : '~'.~.'~' : )
                               |_|    |___/   ~ .~ (   ) ~. ~
                                               (  : '~' :  )
                                                '~ .~~~. ~'
                                                    '~'
   _____            _             _ _           
  / ____|          | |           | | |          
 | |     ___  _ __ | |_ _ __ ___ | | | ___ _ __ 
 | |    / _ \| '_ \| __| '__/ _ \| | |/ _ | '__|
 | |___| (_) | | | | |_| | | (_) | | |  __| |   
  \_____\___/|_| |_|\__|_|  \___/|_|_|\___|_| 

    ''')
    sleep(2)
    

    
def broadcastfinder():
    print('Searching for server....')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 50010))
    data, wherefrom = s.recvfrom(1500, 0)
    #print (data + " " + repr(wherefrom[0]))
    return(wherefrom[0])


def grablist(ipaddress): #Job is to grab the list off the server of connected clients
    gotdata = False
    while gotdata == False: #Will loop till it gets reply from the server
        try:
            message = 'RequestList'
            host = ipaddress #Currently hardcoded that the server is on the same machine as the client
            port = 50000
            size = 1024
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((host,port))
            s.send(message)
            data = s.recv(size)
            data = json.loads(data)
            s.close()
            gotdata = True
            return data
        except socket.error:
            print('Can not find server, trying again')
            sleep(2)

def transmiter(message, ip):
    port = 50008
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print((ip,port))
    s.connect((ip,port))
    s.send(message)
    sleep(0.2)
    s.close()

def ipmenu(ip):
    clearer()
    menurun = True
    while menurun == True:
        print('What would you like to do with this Raspberry Pi?')
        print('Currently connected to ' + str(ip))
        print('')
        print('1. Reboot')
        print('2. Shutdown')
        print('3. Connect via Scratch GPIO')
        print('4. Assign a name')
        print('5. Flash LEDs on robot')
        print('6. Alive check')
        print('7. Disable all GPIO')
        print('8. Return to main menu')


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
            message = 'name :' + name
        elif answer == '5':
            message = 'LED'
        elif answer == '6':
            message = 'Ping'
        elif answer == '7':
            message = 'GPIOoff'
        elif answer == '8':
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
            transmiter(message, ip)
            
        

def menu(clientlist, ipaddress):
    clearer()
    print('Shrimpy classroom management text client')
    print('')
    print('1. Refresh')
    print('2. Reboot all robots')
    print('3. Shut down all robots')
    print('4. Kill all GPIO pins')
    print('')
    print('Connected Raspberry Pis')
    #print('')
    for clientnum in range(0, len(clientlist)):
        print(str(clientnum + 5) + '. ' + clientlist[clientnum])
    answer = raw_input()


    if answer == '1':
        clientlist = grablist(ipaddress)
    elif answer == '2':
        for clientnum in range(0, len(clientlist)):
          transmiter('Reboot', clientlist[clientnum])

    elif answer == '3':
        for clientnum in range(0, len(clientlist)):
          transmiter('Shutdown', clientlist[clientnum])
    elif answer == '4':
        for clientnum in range(0, len(clientlist)):
          print(clientnum)
          print(clientlist[clientnum])
          transmiter('GPIOoff', clientlist[clientnum])
            
    elif (not(int(answer) == 1)) and ((int(answer) - 4) < (len(clientlist)+1)):
        print('Valid')
        ipmenu(clientlist[(int(answer) -6 )])


    menu(clientlist, ipaddress)

startupimage2()
ipaddress = broadcastfinder()
#print('Attempting to connect to server')
clientlist = grablist(ipaddress)
menu(clientlist, ipaddress)
