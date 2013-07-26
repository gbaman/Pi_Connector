import os, socket, json
from time import sleep

def clearer():
    os.system('cls' if os.name=='nt' else 'clear')

def grablist():
    message = 'RequestList'
    host = 'localhost'
    port = 50000
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send(message)
    data = s.recv(size)
    data = json.loads(data)
    s.close()
    #print(data)
    return data

def transmiter(message, ip):
    port = 50007
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
        print('7. Return to main menu')


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
            message = name
        elif answer == '5':
            message = 'LED'
        elif answer == '6':
            message = 'Ping'
        elif answer == '7':
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
            
        

def menu(clientlist):
    clearer()
    print('Shrimpy classroom management text client')
    print('')
    print('1. Refresh')
    for clientnum in range(0, len(clientlist)):
        print(str(clientnum + 2) + '. ' + clientlist[clientnum])
    answer = raw_input()


    if answer == '1':
        clientlist = grablist()
    elif (not(int(answer) == 1)) and ((int(answer) - 1) < (len(clientlist)+1)):
        print('Valid')
        ipmenu(clientlist[(int(answer) -2 )])


    menu(clientlist)


clientlist = grablist()
menu(clientlist)
