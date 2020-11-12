#! /bin/sh
taskNum=1 #任务数

interval=60 #扫描周期
LoginName=`whoami`



ftp_down() {
  for i in `seq $taskNum` 
  do
    NUM=`ps aux | grep "ftp_down.py "$i| grep python3 | grep -v grep | grep $LoginName|wc -l`
    if [ "${NUM}" -lt "1" ];then
      echo "Start ftp_down "$i"......"
      nohup python3 ftp_down.py $i>/dev/null 2>&1 &
      sleep 1
      NUM=`ps aux | grep "ftp_down.py "$i| grep python3 | grep -v grep | grep $LoginName|wc -l`
      if [ "${NUM}" -lt "1" ];then
        echo "ftp_down "$i" start fail......."
      else
	echo "ftp_down "$i" start sucess......."
      fi
    fi  
  done
}

while true ;
do
  ftp_down
  sleep $interval
done
exit 0
