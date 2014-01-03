#! /usr/bin/python

Server_dead_timeout = 23 #In seconds

import traceback
import sys
from time import sleep
from time import time
from socket import *
from subprocess import Popen, call
import threading
import json
try:
    import RPi.GPIO as GPIO
except ImportError:
    print('Raspberry Pi GPIO library not found')  #Catches errors from running on a non Raspberry Pi

def getserial():
  # Extract serial from cpuinfo file to return
  cpuserial = "0000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[22:26]
    f.close()
  except:
    cpuserial = "0000"

  return cpuserial


def transmiter(message, ip, payload = None, expecting = False, port = 50008):
    #port = 50008
    size = 1024
    s = socket(AF_INET, SOCK_STREAM)
    print((ip,port))
    s.connect((ip,port))
    s.send(json.dumps(message, payload))
    sleep(0.2)
    if expecting:
        data = json.loads(s.recv(size))
        return data
    else:
        return None
    s.close()

def register(serverip):
    message = ('Register', str(getserial()))
    host = serverip
    port = 50000
    size = 1024
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.connect((host,port))
    s.send(json.dumps(message))
    data = s.recv(size)
    s.close()
    print('Register socket closed')
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
    if data[0] == 'Reboot':
        print('Rebooting')
        call(['sudo', 'reboot'])
    elif data[0] == 'Shutdown':
        print('Shutting down')
        call(['sudo', 'halt'])
    elif data[0] == 'Scratch':
        print('Activating scratch')
        p = Popen(['sudo', 'python', '/home/pi/simplesi_scratch_handler/scratch_gpio_handler2.py', str(ip[0])])
        #global scratchstat
        #scratchstat = '1'
        #transmiter('scratchactive', ip)
        #p.kill()
    elif data[0] == 'Name':
        print('Feature not implemented yet')
    elif data[0] == 'LED':
        print('LEDs lighting')
        flasher
    elif data[0] == 'GPIOoff':
        allpinsoff()
    elif data[0] == 'CameraFeed':
        call(['raspivid -t 999999 -h 720 -w 1080 -fps 25 -hf -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.3 port=5000'])
        #call(['raspivid', '-t', '999999',  '-h', '720', '-w', '1080', '-fps', '25', '-hf', '-b', '2000000', '-o', '-', '|', 'gst-launch-1.0', '-v', 'fdsrc', '!', 'h264parse', '!',  'rtph264pay', 'config-interval=1', 'pt=96', '!', 'gdppay', '!', 'tcpserversink', 'host=10.0.5.167', 'port=5000'])
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

def flasher():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.OUT)
    GPIO.output(11,True)
    sleep(1)
    GPIO.output(11,False)

def pingreplyer(lastping, Server_dead_timeout):
    HOST = ''  
    PORT = 50008
    #s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Defining the network interface
    bound = False
    while bound == False:
        try:
            s.bind((HOST,PORT))
            bound = True
        except error:
            print('Bind failed, will retry in 5 seconds')
            sleep(5)
            bound = False
        
    s.settimeout(10)
    outloopdone = False
    while outloopdone == False:
        
        s.listen(2) #Waits for a connection to be made to the socket, max 2 connections.
        try:
            conn, addr = s.accept()
            #print 'Connected by', addr
            print('Pinged by server at ' + str(addr[0]))
            sleep(0.05)
            data = json.loads(conn.recv(1024))
            if not data: break
            print(data[0])
            #print(data[1])
            if data[0] == 'Ping':
                conn.sendall(json.dumps(('Alive',str(getserial()))))
                lastping = time()
            else:
                interpreter(data, addr)
            #conn.close()
            #print('Print ping 1 conn closed')
            #s.close()
            #print('Print ping 1 s closed')
        except timeout:
            #try:
                #print('Timed out, oh dear....')
                #conn.close()
                #print('Print ping 2 conn closed')
                #s.close()
                #print('Print ping 2 s closed')
            #except UnboundLocalError:
                #s.close()
                #print('Print ping 2 s closed')
            pass
        #print((time() - lastping))
        if (time() - lastping > Server_dead_timeout):
            print('')
            print('-------------------------------------------------------------------------')
            print('Server must have died, have not been pinged in over ' + str(Server_dead_timeout) + ' seconds')
            print('-------------------------------------------------------------------------')
            print('')
            outloopdone = True
    try:
        conn.close()
        print('Ping 1 conn closed')
    except:
        pass
    s.close()
    print('Ping 2 conn closed')
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
    try:
        serverip = broadcastfinder()
        lastping = register(serverip)
        lastping = pingreplyer(lastping, Server_dead_timeout)
    except: # (not KeyboardInterrupt):
        print('************************************')
        print("System error...")
        traceback.print_exc(file=sys.stdout) #Prints out traceback error
        print('************************************')
        print("")
        sleep(1)
        print("RESTARTING")
        sleep(3)