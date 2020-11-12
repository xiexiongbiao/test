#! /bin/sh
LoginName=`whoami`

if [ "$#" = "0" ]
then
	echo "nohup sh start_ftp_down.sh [task_id] &"
	exit 0
fi

ftp_down() {
  NUM=`ps aux | grep "\<ftp_down.py "$1"\>"| grep python3 | grep -v grep | grep $LoginName|wc -l`
  if [ "${NUM}" -lt "1" ];then
    echo "Start ftp_down "$1"......"
    nohup python3 ftp_down.py $1>/dev/null 2>&1 &
    sleep 1
    NUM=`ps aux | grep "\<ftp_down.py "$1"\>"| grep python3 | grep -v grep | grep $LoginName|wc -l`
    if [ "${NUM}" -lt "1" ];then
	  echo "ftp_down "$1" start fail......."
    else
	  echo "ftp_down "$1" start sucess......."
    fi
  fi
}

NUM=`ps aux | grep "\<sh start_ftp_down.sh "$1"\>"|grep -v grep | grep $LoginName|wc -l`
if [ "${NUM}" -gt "2" ];then
  echo $NUM
  echo "start_ftp_down $1 is already running"
  exit 0
fi

while true ;
do
  ftp_down $1
  sleep 60
done
exit 0
