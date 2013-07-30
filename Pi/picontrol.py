#! /usr/bin/python

Server_dead_timeout = 20 #In seconds


from time import sleep
from time import time
from socket import *
from subprocess import Popen, call
try:
    import RPi.GPIO as GPIO
except ImportError:
    print('Raspberry Pi GPIO library not found')  #Catches errors from running on a non Raspberry Pi


def register(serverip):
    message = 'Register'
    host = serverip
    port = 50000
    size = 1024
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.connect((host,port))
    s.send(message)
    data = s.recv(size)
    s.close()
    #print 'Received:', data 
    #print(data)
    if data == 'Accept':
        print('')
        print('----------------------------------------')
        print('Connected to server at ' + str(serverip))
        print('----------------------------------------')
        print('')
    lastping = time()
    return lastping
    #print(data[1])

def interpreter(data, ip):
   if data == 'Reboot':
	print('Rebooting')
	call(['sudo', 'reboot'])
   elif data == 'Shutdown':
	print('Shutting down')
	call(['sudo', 'halt'])
   elif data == 'Scratch':
	print('Activating scratch')
	p = Popen(['sudo', 'python', 'simplesi_scratch_handler/scratch_gpio_handler2.py', str(ip[0])])
	sleep(2)
   elif data[0:3] == 'Name':
	print('Feature not implemented yet')
   elif data == 'LED':
	print('LEDs lighting')
   elif data == 'GPIOoff':
        allpinsoff()
   else:
	print('Invalid message')



def allpinsoff():
    pinlist = [3, 5, 7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26] #List of pins on the Raspberry Pi
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    for pinnum in range(0, (len(pinlist))):
        print('Pin ' + str(pinlist[pinnum]) + ' ' + str(pinnum))
        GPIO.setup((pinlist[pinnum]),GPIO.OUT) #Disables each pin one at a time
        GPIO.output((pinlist[pinnum]), False)
    GPIO.cleanup()



def pingreplyer(lastping, Server_dead_timeout):
    HOST = ''  
    PORT = 50008
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Defining the network interface
    s.bind((HOST,PORT))
    s.settimeout(10)
    outloopdone = False
    while outloopdone == False:
        
        s.listen(2) #Waits for a connection to be made to the socket, max 2 connections.
        try:
            conn, addr = s.accept()
            #print 'Connected by', addr
            print('Pinged by server at ' + str(addr[0]))
            data = conn.recv(1024)
            if not data: break
            if data == 'Ping':
                conn.sendall('Alive')
                lastping = time()
            else:
                interpreter(data, addr)
            conn.close()
        except timeout:
            #print('Timed out, oh dear....')
            conn.close()
        #print((time() - lastping))
        if (time() - lastping > Server_dead_timeout):
            print('')
            print('-------------------------------------------------------------------------')
            print('Server must have died, have not been pinged in over ' + str(Server_dead_timeout) + ' seconds')
            print('-------------------------------------------------------------------------')
            print('')
            outloopdone = True
    s.close()
    return(lastping)
    
    



def broadcastfinder():
    print('Searching for server...')
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 50010))
    data, wherefrom = s.recvfrom(1500, 0)
    #print (data + " " + repr(wherefrom[0]))
    return(wherefrom[0])

#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lastping = int(time())
while 1:
    serverip = broadcastfinder()
    lastping = register(serverip)
    lastping = pingreplyer(lastping, Server_dead_timeout)
