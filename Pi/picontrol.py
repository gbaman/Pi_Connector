#! /usr/bin/python


from time import sleep
from socket import *
from subprocess import Popen, call
def register(serverip):
    message = 'Register'
    host = serverip
    port = 50000
    size = 1024
    s = socket(AF_INET, SOCK_STREAM)
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
	sleep(0.2)
   elif data == 'Name':
	pass
   elif data == 'LED':
	print('LEDs lighting')
   else:
	print('Invalid message')






def pingreplyer():
    #sleep(1)
    while 1:
    
        HOST = ''                 # Symbolic name meaning all available interfaces
        PORT = 50007              # Arbitrary non-privileged port
        s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        print 'Connected by', addr
        while 1:
            data = conn.recv(1024)
	    print(data)
            if not data: break
	    if data == 'Ping':
            	conn.sendall('Alive')
	    else:
		interpreter(data, addr)
        conn.close()

def broadcastfinder():
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 50010))
    data, wherefrom = s.recvfrom(1500, 0)
    print (data + " " + repr(wherefrom[0]))
    return(wherefrom[0])

#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverip = broadcastfinder()
register(serverip)
pingreplyer()
