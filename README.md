Pi_Connector
============

Pi_connector is a backend system for controlling Raspberry Pis (and possibly other Linux based operating systems). It features a simple commandline based frontend for managing the system, user accounts and a permission based menu system. It's main use though is running BASH commands on a single or multiple Raspberry Pis. Want to add a new command? Check the large comment at the top of ```server.py```.   
   
There is 3 main sections to the program.   
A server, a client and the software that runs on all your Raspberry Pis.   
All the code has only been tested on Unix based OSs (Linux, Mac OS etc), may not work reliably under windows.  
   
Installation
=============
   
```git clone https://github.com/gbaman/Pi_Connector```    
```cd Pi_Connector```   
   
The server   
```python setup.py standalone server```
   
The textclient   
```python setup.py standalone client```   
   
The daemon (to run on pis)   
```python setup.py standalone picontrol```   
   
Everything on the one machine   
```python setup.py standalone full```   
   
To uninstall everything   
```python setup.py standalone remove```  
   
   
How to use
============
   
To launch the server, open a terminal and type ```raspiServer```   
To launch the textclient, open a terminal and type ```raspiClient```   
The daemon should automatically launch, to restart it, use   
```service picontrol.sh stop``` and ```service picontrol.sh start```

