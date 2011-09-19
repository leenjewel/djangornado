#!/bin/bash

project_name=""
work_path=""
log_path=$work_path/log

case $1 in 
    start)
        echo "**************************"
        echo "*  Djangornado           *"
        echo "**************************"
        echo "**  Warning:"
        echo "**  When you start djangornado web server with daemon, You must set \"DEBUG = False\" in your settings of project."
        echo "**  Waiting..."
        python $work_path/manage.py rundaemon \
            pnum=4    \
            method=prefork    \
            host="0.0.0.0"    \
            port=80    \
            pidfile=$log_path/djangornado.pid    \
            outlog=$log_path/out.log    \
            errlog=$log_path/err.log
        echo "Service is running."
    ;;
    stop)
        echo "**  Waiting..."
        for pid in `cat $log_path/djangornado.pid`; do 
            kill -9 $pid
        done
        for pid in `ps aux | grep python | grep $project_name | awk -F ' ' '{print $2'}`; do 
            kill -9 $pid
        done
        echo "**  Service is stop."
    ;;
    restart)
        $0 stop
        sleep 1
        $0 start
    ;;
    *)
        echo "usage: $0 {start|stop|restart}"
esac
exit 0