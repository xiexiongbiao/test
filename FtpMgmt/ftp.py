from ftplib import FTP
from ftplib import error_perm
import socket

def get_ftp_time(ftp,file):
    try:
        ftp_time = ftp.sendcmd('MDTM ' + file)
    except error_perm as fe:
        return False,str(fe)
    ftp_time = ftp_time.split(" ")[1]
    return True,ftp_time

def open_ftp(login):
    try:
        ftp = FTP()
        ftp.set_pasv(login["passive"])  # 1 使用被动模式，0 主动模式
        ftp.connect(login["host"], login["port"])
        ftp.encoding = 'gbk'
        ftp.login(login["user"], login["password"])
    except(socket.error, socket.gaierror):  # ftp 连接错误
        err_msg = "ERROR: cannot connect [{}:{}]".format(login["host"], login["port"])
        return None,err_msg
    except error_perm:  # 用户登录认证错误
        err_msg = "ERROR: user Authentication failed "
        return None,err_msg
    return ftp,""
