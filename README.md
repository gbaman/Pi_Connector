Pi_Connector
============

Connector software for a collection of headless Raspberry Pis
The software does not require any IP addresses and will automatically find each other.


How to use
============

Clone the repository.
There is 3 main sections to the program.
A server, a client and the software that runs on all your Raspberry Pis.

All the code has only been tested on Unix based OSs (Linux, Mac OS etc), may not work reliably under windows.


Copy the picontrol.py over to the pi to /usr/local/bin/picontrol.py
Then copy picontrol.sh to /etc/init.d/picontrol.sh
Make it executable sudo chmod 755 /etc/init.d/picontrol.sh 
Finally, update your OS for your script to run on boot sudo update-rc.d picontrol.sh defaults

Next reboot your pi and run the server on a separate machine. The picontrol.py script cannot be run on the same computer as the server. The client though can run on the same machine as the server and in this current release is required to be.

Once the Pi reboots, as long as the server is running on the network, the pi should register with the server, refresh the text client and it should be in the list.
Not all functions work currently, reboot and shutdown work fine while scratch GPIO is a bit buggy. Name, LEDs and Alive check do not currently work in this release.

Current Bugs
============
- Assign name, Flash LEDs and Alive check currently do not work.
- Scratch GPIO has no check if you currently have it installed
- Scratch GPIO crashes client
- A large amount of debug info still exists.
- Code isn't commented yet much

Changelog
============
0.1 - Initial release - 26.7.2013 - Danger, very buggy
0.2 - 29.7.2013 - Still very buggy, fixed auto reconnect and added splash screen
0.2.1 - 30.7.2013 - Still very buggy, rewrote pinger and fixed auto reconnect again...