#! /usr/bin/python


from time import sleep
from time import time
from socket import *
from subprocess import Popen, call
import RPi.GPIO as GPIO


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
    print 'Received:', data 
    print(data)
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
   elif data == 'Name':
	pass
   elif data == 'LED':
	print('LEDs lighting')
   elif data == 'GPIOoff':
        allpinsoff()
   else:
	print('Invalid message')



def allpinsoff():
    pinlist = [3, 5, 7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26]
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    for pinnum in range(0, (len(pinlist))):
        print('Pin ' + str(pinlist[pinnum]) + ' ' + str(pinnum))
        GPIO.setup((pinlist[pinnum]),GPIO.OUT)
        GPIO.output((pinlist[pinnum]), False)
    GPIO.cleanup()


def pingreplyer():
    #sleep(1)
    while 1:
        
    
        HOST = ''                 # Symbolic name meaning all available interfaces
        PORT = 50007              # Arbitrary non-privileged port
        s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #s.bind((HOST, PORT))
	print(gethostname())
	s.bind((HOST,50008))
        s.settimeout(10)
        s.listen(1)
        try:
            conn, addr = s.accept()
            print 'Connected by', addr
            print 'Connected by', addr
            lastping = time()
            while 1:
                if (time() - lastping) > 30:
                    print('breaking')
                    break
                data = conn.recv(1024)
                print(data)
                if not data: break
                if data == 'Ping':
                    conn.sendall('Alive')
                    lastping = time()
                else:
                    interpreter(data, addr)
            conn.close()
        except timeout:
            print('Timed out, oh dear....')
            s.close()
            break
            #s.shutdown()
            #sleep(1)
            #pingreplyer()
            #s.close()
            #s.shutdown()

def broadcastfinder():
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 50010))
    data, wherefrom = s.recvfrom(1500, 0)
    print (data + " " + repr(wherefrom[0]))
    return(wherefrom[0])

#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
while 1:
    serverip = broadcastfinder()
    register(serverip)
    pingreplyer()
