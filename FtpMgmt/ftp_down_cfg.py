
FtpInfo = {}
Delivery = {}
Tasks = {}

FtpInfo[1] = {  # 远程主机的ftp登录信息
    "host" : "192.168.22.22",
    "port" : 21,
    "user" : "sss",
    "password" : "ssss",
    "passive" : 1 # (1 使用被动模式，0 主动模式)
}

Delivery[1] = {
    "source" : {  # 源主机存放路径，路径必须已存在，且为绝对路径
        "host" : FtpInfo[1],
        "root_dir" : "/home/bossnm/tests/source", # 远程主机文件存放路径
        "backup_dir" : "/home/bossnm/tests/backup", # 远程主机文件备份路径
    },
    "target" : {  # 本地存放路径
        "root_dir" : "/root/FtpMgmt/ftpdata/store", # 本地主机文件存放路径 (路径已固化在镜像中，无需配置)
        "tmp_dir" : "/root/FtpMgmt/ftpdata/tmp" # 本地主机文件存放临时路径 (路径已固化在镜像中，无需配置)
    }
}

Tasks[1] = {
    "delivery" : Delivery[1],
    "interval" : 300    # 任务执行时间间隔，单位：秒
}
