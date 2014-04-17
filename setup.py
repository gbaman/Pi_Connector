import os
import sys
from shutil import copy2
from subprocess import call

def usage():
    print("")
    print("-------------------------------------------------------------------------------")
    print("")
    print("To use this installer, parameters are required")
    print("1st parameter is ltsp or anything else. If ltsp is used, will install for LTSP")
    print("2nd parameter is what to install, available options are")
    print("server, client, picontrol, full, remove")
    print("remove uninstalls everything")
    print("")
    print("-------------------------------------------------------------------------------")
    print("")



def installMenu():
    print("What would you like to do?")
    print("Please note, this installer assumes Debian Wheezy")

    print("")
    print("1. Install Server")
    print("2. Install textclient")

def installTextClient(ltsp = False):
    global root
    if ltsp:
        copy2(root + "Client/textclient.py" ,"/opt/ltsp/armhf/usr/local/bin/raspiClient")
        call(["sudo", "chmod", "755", "/opt/ltsp/armhf/usr/local/bin/raspiClient"])

    else:
        copy2(root + "Client/textclient.py" ,"/usr/local/bin/raspiClient")
        call(["sudo", "chmod", "755", "/usr/local/bin/raspiClient"])

def installServer(ltsp = False):
    global root
    copy2(root + "Server/server.py", "/usr/local/bin/raspiServer")
    copy2(root + "Server/piserver.sh", "/usr/local/bin/piserver")
    call(["chmod", "755", "/usr/local/bin/raspiServer"])
    call(["chmod", "755", "/usr/local/bin/piserver"])
    #call(["update-rc.d", "piserver.sh", "defaults"])
    #call(["service", "piserver.sh", "start"])


def installPicontrol(ltsp = False):
    global root
    if ltsp:
        copy2(root + "Pi/picontrol.py", "/opt/ltsp/armhf/usr/local/bin/picontrol.py")
        copy2(root + "Pi/picontrol.sh", "/opt/ltsp/armhf/etc/init.d/picontrol.sh")
        copy2(root + "Pi/get-display", "/opt/ltsp/armhf/usr/local/bin/get-display")
        copy2(root + "Pi/lock-screen", "/opt/ltsp/armhf/usr/local/bin/lock-screen")
        copy2(root + "Pi/lock.svg", "/opt/ltsp/armhf/usr/local/bin/lock.svg")
        call(["chmod", "755", "/opt/ltsp/armhf/etc/init.d/picontrol.sh"])
        call(["chmod", "755", "/opt/ltsp/armhf/usr/local/bin/picontrol.py"])
        call("ltsp-chroot --arch armhf update-rc.d picontrol.sh defaults" ,  shell=True)
    else:
        copy2(root + "Pi/picontrol.py", "/usr/local/bin/picontrol.py")
        copy2(root + "Pi/picontrol.sh", "/etc/init.d/picontrol.sh")
        copy2(root + "Pi/get-display", "/usr/local/bin/get-display")
        copy2(root + "Pi/lock-screen", "/usr/local/bin/lock-screen")
        copy2(root + "Pi/lock.svg", "/usr/local/bin/lock.svg")
        call(["chmod", "755", "/opt/ltsp/armhf/etc/init.d/picontrol.sh"])
        call(["chmod", "755", "/usr/local/bin/picontrol.py"])



def checkWhere():
    if (os.path.isdir("Client")) and os.path.isdir("Pi") and os.path.isdir("Server"):
        return ""
    elif os.path.isdir("Pi_Connector"):
        return "Pi_Connector/"
    else:
        call(["git", "clone", "https://github.com/gbaman/Pi_Connector.git"])
        return "Pi_Connector/"

def deleteAll(ltsp = False):
    if ltsp:
        call(["service", "piserver.sh", " stop"])
        try:
            os.remove("/opt/ltsp/armhf/usr/local/bin/raspiClient")
        except:
            print("raspiClient not found")
        try:
            os.remove("/usr/local/bin/raspiServer")
            os.remove("/usr/local/bin/piserver.sh")
        except:
            print("piserver.sh or raspiServer not found")
        try:
            os.remove("/opt/ltsp/armhf/usr/local/bin/picontrol.py")
            os.remove("/opt/ltsp/armhf/etc/init.d/picontrol.sh")
            os.remove("/opt/ltsp/armhf/usr/local/bin/get-display")
            os.remove("/opt/ltsp/armhf/usr/local/bin/lock-screen")
            os.remove("/opt/ltsp/armhf/usr/local/bin/lock.svg")
        except:
            print("picontrol not found")
    else:
        call(["service", "piserver.sh", " stop"])
        try:
            os.remove("/usr/local/bin/raspiClient")
        except:
            print("raspiClient not found")
        try:
            os.remove("/usr/local/bin/raspiServer")
            os.remove("/etc/init.d/piserver")
        except:
            print("piserver.sh or raspiServer not found")
        try:
            os.remove("/usr/local/bin/picontrol.py")
            os.remove("/etc/init.d/picontrol.sh")
            os.remove("/usr/local/bin/get-display")
            os.remove("/usr/local/bin/lock-screen")
            os.remove("/usr/local/bin/lock.svg")
        except:
            print("picontrol not found")

if not os.geteuid()==0:
    sys.exit("\nOnly root can run this script\n")


root = checkWhere()
#print(sys.argv)
if (len(sys.argv) > 1 ):
    if sys.argv[1] == "ltsp":
        ltsp = True
    else:
        ltsp = False
    if sys.argv[2] == "client":
        installTextClient(ltsp)
    elif sys.argv[2] == "server":
        installServer(ltsp)
    elif sys.argv[2] == "picontrol":
        installPicontrol(ltsp)
    elif sys.argv[2] == "full":
        installServer(ltsp)
        installPicontrol(ltsp)
        installTextClient(ltsp)
    elif sys.argv[2] == "remove":
        print("deleting")
        deleteAll(ltsp)
else:
    usage()