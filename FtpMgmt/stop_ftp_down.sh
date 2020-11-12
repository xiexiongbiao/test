#!/bin/sh
LoginName=`whoami`

echo "stop ftp_down all"
`ps aux | grep -E 'ftp_down' | grep -v grep | grep $LoginName| awk '{print $2}' | xargs kill -9 &> /dev/null`
ret=$?
if [ $ret -eq 0 ]; then
	echo "stop ftp_down all success"
else
	echo "stop ftp_down all failure"
fi

