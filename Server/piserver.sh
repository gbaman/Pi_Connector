### BEGIN INIT INFO
# Provides: PI controller script.
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Raspberry Pi controller 
# Description: Control of a collection of Raspberry Pis
### END INIT INFO


#! /bin/sh
# /etc/init.d/picontrol.sh


export HOME
case "$1" in
    start)
        echo "Starting Server"
        /usr/local/bin/raspiServer.py > /dev/null 2>&1 &
    ;;
    stop)
        echo "Stopping Server"
        LCD_PID=`ps auxwww | grep raspiServer.py | head -1 | awk '{print $2}'`
        kill -9 $LCD_PID
    ;;
    *)
        echo "Usage: /etc/init.d/picontrol {start|stop}"
        exit 1
    ;;
esac
exit 0
