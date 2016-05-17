#!/bin/bash
#Author=Weiliang,Wu
python_prog="/usr/local/bin/python3"
DIR="$( cd "$( dirname "$0"  )" && pwd  )"
pid=`ps aux|grep -v grep|grep CoreLinkListener.py|awk '{print $2}'`
entry_location=`ps aux|grep -v grep|grep CoreLinkListener.py|awk '{print $12}'`
memusage=`ps aux|grep -v grep|grep CoreLinkListener.py|awk '{print $4}'`
cpuusage=`ps aux|grep -v grep|grep CoreLinkListener.py|awk '{print $3}'`
reload() {
    if [[ $pid != '' ]] ; then
        if [[ $entry_location != $DIR/CoreLinkListener.py ]] ; then
            echo 'Although an instance of CoreLinkListener can be found, it does not belong to this script!'
            echo 'Try putting this script in the same folder of your CoreLinkListener.py'
            exit -1
        fi
        kill -s 5 $pid
        $python_prog $DIR/CoreLinkListener.py --shell >> $DIR/log.log 2>&1 &
        newpid=`ps aux|grep -v grep|grep CoreLinkListener.py|awk '{print $2}'`
        if [[ $newpid != '' ]] ; then
            echo 'Successfully restart the CoreLinkListener Program ( PID' $newpid ')'
        fi
    else
        echo 'No instance of current running CoreLinkListener Program can be found!'
    fi
}

start(){
    if [[ $pid == '' ]] ; then
        echo $python_prog $DIR
        $python_prog $DIR/CoreLinkListener.py --shell >> $DIR/log.log 2>&1 &
        newpid=`ps aux|grep -v grep|grep CoreLinkListener.py|awk '{print $2}'`
        if [[ $newpid != '' ]] ; then
            echo 'Successfully start the CoreLinkListener Program ( PID' $newpid ')'
        fi
    else
        echo 'An instance of CoreLinkListener can be found. Please stop it first( PID' $pid ')'
    fi
}
stop(){
    if [[ $pid != '' ]] ; then
        if [[ $entry_location != $DIR/CoreLinkListener.py ]] ; then
                echo 'Although an instance of CoreLinkListener can be found, it does not belong to this script!'
                echo 'Try putting this script in the same folder of your CoreLinkListener.py'
                exit -1
        fi
        kill -s 5 $pid
        echo 'Successfully stop the CoreLinkListener Program ( PID' $pid ')'
    else
        echo 'No instance of current running CoreLinkListener Program can be found!'
    fi

}

check(){
    if [ `echo $memusage "> 20"|bc` -eq 1 ] ; then
        echo 'Start reloading the CoreLinkListener Program as overusing memory'
        reload
    fi
    if [ `echo $cpuusage "> 80"|bc` -eq 1 ] ; then
        echo 'Start reloading the CoreLinkListener Program as overusing CPU'
        reload
    fi
    if [[ $pid == '' ]] ; then
        echo 'No instance of current running CoreLinkListener Program can be found! It will be started.'
        start
    fi
}

#Passing argument to control the program
case $1 in
    "start")
        start
    ;;
    "reload")
        reload
    ;;
    "stop")
        stop
    ;;
    "check")
        check
    ;;
    *)
        echo 'Usage: '$0' start|reload|stop|check'
    ;;
esac
