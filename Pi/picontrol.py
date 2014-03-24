#!/usr/bin/python

active = True
Server_dead_timeout = 23 #In seconds

import traceback
import sys
from time import sleep
from time import time
from socket import *
from subprocess import Popen, call, PIPE, STDOUT
import threading
import json
from datetime import datetime
import os.path
import os
import getpass
try:
    import RPi.GPIO as GPIO
    GpioFound = True
except ImportError:
    print('Raspberry Pi GPIO library not found')  #Catches errors from running on a non Raspberry Pi
    GpioFound = False

class backgroundLock(threading.Thread):
    def __init__(self):
        super(backgroundLock, self).__init__()
    def run(self):
        call(["export $(sh get-display) && python lock-screen"], shell=True)




def getActiveUser():
    who = Popen(['who'],stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    result = who.stdout.read()
    result = result.split("   ")
    return result[0]


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
    #print((ip,port))
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
    message = ('Register', str(getserial()), str(getActiveUser()))
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
    global screenLock
    if data[0][0] == 'Reboot':
        print('Rebooting')
        if active:
            call(['sudo', 'reboot'])
    elif data[0][0] == 'Shutdown':
        print('Shutting down')
        if active:
            call(['sudo', 'halt'])
    elif data[0][0] == 'Scratch':
        print('Activating scratch')
        p = Popen(['sudo', 'python', '/home/pi/simplesi_scratch_handler/scratch_gpio_handler2.py', str(ip[0])])
    elif data[0][0] == 'LED':
        print('LEDs lighting')
        #flasher()
    elif data[0][0] == 'GPIOoff':
        allpinsoff()
    elif data[0][0] == 'CameraFeed':
        call(['raspivid -t 999999 -h 720 -w 1080 -fps 25 -hf -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.3 port=5000'])
    elif data[0][0] == "ScreenLock":
        try:
            c = backgroundLock()
            c.daemon = True
            c.start()
        except:
            print("this command has crashed")
    elif data[0][0] == "ScreenUnlock":
        if active:
            call(["pkill -f 'python lock-screen'"],shell=True)
    elif data[0][0] == "BatchCommand":
        try:
            print("Running command " + str(data[0][1][0]))
            if active:
                call([data[0][1][0]])
        except:
            print("Unknown command!")

    else:
        print('Invalid message')
        print(data)



def allpinsoff():
    if GpioFound:
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
    if GpioFound:
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11,GPIO.OUT)
        GPIO.output(11,True)
        sleep(1)
        GPIO.output(11,False)
    else:
        print(GpioFound)

def pingreplyer(lastping, Server_dead_timeout):
    global conn
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
            print('Pinged by server at ' + str(addr[0]) + ' at ' + str(datetime.now().strftime('%H:%M:%S')))
            sleep(0.05)
            data = json.loads(conn.recv(1024))
            if not data: break
            if data[0] == 'Ping':
                conn.sendall(json.dumps(('Alive',str(getserial()))))
                lastping = time()
            else:
                #print(data)
                interpreter(data, addr)
                #print("interpreter done")
        except timeout:
            print("There has been a timeout...")
        if (time() - lastping > Server_dead_timeout):
            print('')
            print('-------------------------------------------------------------------------')
            print('Server must have died, have not been pinged in over ' + str(Server_dead_timeout) + ' seconds')
            print('-------------------------------------------------------------------------')
            print('')
            outloopdone = True
    try:
        assert isinstance(conn, object)
        conn.close()
        print('Ping 1 conn closed')
    except:
        pass
    s.close()
    print('Ping 2 conn closed')
    return(lastping)
    
class mainC(threading.Thread):
    def __init__(self):
        super(mainC, self).__init__()
    def run(self):
        self.mainController()
    def mainController(self):
        lastping = int(time())
        while 1:
            #try:
            serverip = broadcastfinder()
            lastping = register(serverip)
            lastping = pingreplyer(lastping, Server_dead_timeout)
            #except:
            #    print("exception")
            #    break


def broadcastfinder():
    print('Searching for server...')
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 50011))
    data, wherefrom = s.recvfrom(1500, 0)
    #print (data + " " + repr(wherefrom[0]))
    return(wherefrom[0])

def fetchLibs():
    if not os.path.isfile("lock-screen"):
        call(['wget', 'http://bazaar.launchpad.net/~epoptes/epoptes/trunk/download/head:/lockscreen-20110927210214-xi0yyacred1dmjl5-40/lock-screen'])
        call(['wget', 'http://bazaar.launchpad.net/~epoptes/epoptes/trunk/download/head:/lock.svg-20110927210214-xi0yyacred1dmjl5-41/lock.svg'])
    if not os.path.isfile("get-display"):
        pass

#---------------------------------------------------------------------------------Main Program----------------------------------------------------------------------------------


#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#threading.Thread(mainController())
os.chdir(os.path.dirname(sys.argv[0]))
fetchLibs()
m = mainC()
#m.daemon = True
#m.start()
m.run()


""" except: # (not KeyboardInterrupt):
        print('************************************')
        print("System error...")
        traceback.print_exc(file=sys.stdout) #Prints out traceback error
        print('************************************')
        print("")
        sleep(1)
        print("RESTARTING")
        sleep(3) """