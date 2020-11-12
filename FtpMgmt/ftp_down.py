import sys,os,time,re,shutil,logging
import ftplib,signal,pymysql
import traceback
import config,ftp_db
from ftp_down_cfg import *
from ftp import *

taskId = int(sys.argv[1])
logger = config.logger('ftp_down_'+str(taskId), **config.logger_args)

# if len(sys.argv) < 2:
#     print("启动参数任务ID必需")
#     exit()

def checkLocalPath():
    if not (os.path.exists(Tasks[taskId]["delivery"]["target"]["root_dir"])):
        err_msg = "任务Tasks[%d]的本地文件存放目录不存在" % taskId
        return False, err_msg

    if not os.path.exists(Tasks[taskId]["delivery"]["target"]["tmp_dir"]):
        err_msg = "任务Tasks[%d]的本地临时文件存放目录不存在" % taskId
        return False, err_msg
    return True,""

def checkRemotePath():
    # ftp连接
    ftp,msg = open_ftp(Tasks[taskId]["delivery"]["source"]["host"])
    if not ftp:
        err_msg = "ftp连接失败,失败原因:%s,请检查FtpInfo[%d]配置" % (msg, taskId)
        return False, err_msg

    # 远程目录检查
    try:
        ftp.cwd(Tasks[taskId]["delivery"]["source"]["root_dir"])
    except ftplib.error_perm:
        err_msg = "源主机上的文件存放目录[%s]不存在" % Tasks[taskId]["delivery"]["source"]["root_dir"]
        ftp.close()
        return False,err_msg

    try:
        ftp.cwd(Tasks[taskId]["delivery"]["source"]["backup_dir"])
    except ftplib.error_perm:
        try:
            ftp.mkd(Tasks[taskId]["delivery"]["source"]["backup_dir"])
            logger.info("源主机备份目录[%s]创建成功" % Tasks[taskId]["delivery"]["source"]["backup_dir"])
        except ftplib.error_perm:
            err_msg = "源主机备份目录[%s]创建失败" % Tasks[taskId]["delivery"]["source"]["backup_dir"]
            ftp.close()
            return False, err_msg
    ftp.close()
    return True,""

def checkTask():
    global taskId
    # 任务id检查
    if taskId not in Tasks.keys():
        err_msg = "任务Tasks[%d]未定义" % taskId
        return False,err_msg
    # ftp配置检查
    if taskId not in FtpInfo.keys():
        err_msg = "FtpInfo[%d]未定义" % taskId
        return False, err_msg
    # 配置目录检查
    if taskId not in Delivery.keys():
        err_msg = "Delivery[%d]未定义" % taskId
        return False, err_msg

    # ftp连接和目录校验
    if not Tasks[taskId]["delivery"]["source"]["root_dir"].startswith("/") or \
       not Tasks[taskId]["delivery"]["source"]["backup_dir"].startswith("/") or \
       not Tasks[taskId]["delivery"]["target"]["root_dir"].startswith("/") or \
       not Tasks[taskId]["delivery"]["target"]["tmp_dir"].startswith("/"):
        err_msg = "配置中的路径必须是绝对路径"
        return False, err_msg

    # 本地目录检查
    status,msg = checkLocalPath()
    if not status:
        return False,msg

    # 远程目录检查和远程备份目录检查(不存在则创建)
    status, msg = checkRemotePath()
    if not status:
        return False,msg
    return True,""

def checkFileDir(ftp,file_name):
    """
    判断当前目录下的文件与文件夹
    :param ftp: 实例化的FTP对象
    :param file_name: 文件名/文件夹名
    :return:返回字符串“File”为文件，“Dir”问文件夹，“Unknow”为无法识别
    """
    rec = ""
    try:
        rec = ftp.cwd(file_name)   # 需要判断的元素
        ftp.cwd("..")   # 如果能通过路劲打开必为文件夹，在此返回上一级
    except ftplib.error_perm as fe:
        rec = fe # 不能通过路劲打开必为文件，抓取其错误信息
    finally:
        if "550" in str(rec):
            return "File"
        elif "250" in str(rec):
            return "Dir"
        else:
            return "Unknow"

def parse_filename(filename):
    parse_result = {}
    # filename = "1106_CM_CTZY_OO_IDY_20200910060102_000.tar.gz"
    res = filename.rsplit("_",2)
    if len(res) !=3:
        return None, "[%s]文件不满足[文件名_时间戳_xxx.后缀]的格式" % filename
    parse_result["file_name_prefix"] = res[0]
    parse_result["file_time"]= res[1]
    return parse_result,None

"""
ftp: 实例化的FTP对象
RemoteFile: 要下载的文件名（服务器中）
LocalFile: 本地文件路径
bufsize: 服务器中文件大小 
"""
def ftp_download(ftp,LocalFile, RemoteFile, bufsize):
    try:
        with open(LocalFile, 'wb') as f:
            if bufsize == 0:
                f.close()
                return True,""
            ftp.retrbinary('RETR %s' % RemoteFile, f.write, bufsize)
            f.close()
            return True,""
    except Exception as e:
        err_msg = str(e)
        return False,err_msg

def do_delivery(delivery,ftp):
    db.checkConnect()
    # 打开远程目录
    ftp.cwd(delivery["source"]["root_dir"])
    # 获取该目录下所有文件名，列表形式
    RemoteNames = ftp.nlst()
    fileCnt = 0
    for file in RemoteNames:
        if checkFileDir(ftp,file) == "File":
            fileCnt = fileCnt + 1
            # 开始下载文件
            ftp.voidcmd('TYPE I')  # 将传输模式改为二进制模式 ,避免提示 ftplib.error_perm: 550 SIZE not allowed in ASCII
            bufsize = ftp.size(file)  # 服务器里的文件总大小
            Local = os.path.join(delivery["target"]["tmp_dir"], file)  # 下载到当地的全路径
            status,msg = ftp_download(ftp,Local, file, 1024)
            if status:
                # 将临时文件移动到本地目录
                shutil.move(delivery["target"]["tmp_dir"]+"/" + file,delivery["target"]["root_dir"]+"/" + file)
                # 将远程文件移动到远程备份目录下
                ftp.rename(delivery["source"]["root_dir"]+"/" + file,delivery["source"]["backup_dir"]+"/" + file)
                logger.info("[%s]文件下载成功" % file)

                # 解析文件(文件名称,文件类型,所属系统,文件后缀)exit
                parse_res,msg = parse_filename(file)
                if not parse_res:
                    logger.error("文件名解析失败,失败原因:%s" % msg)
                    continue

                # 根据文件名查询文件相关的信息
                res,msg = db.selectFileinfo(parse_res["file_name_prefix"])
                if res:
                    # 文件信息入mysql数据库
                    status, msg = db.inserFileinfo(res, parse_res["file_time"], bufsize, file)
                    if status:
                        logger.info("[%s]文件信息入库成功" % file)
                    else:
                        logger.error("[%s]文件信息入库失败,失败原因:%s" % (file, msg))
                else:
                    logger.error("从system_config_tbl表查询[%s]文件信息失败,失败原因:%s" % (file,msg))


            else:
                logger.error("[%s]文件下载失败,失败原因:%s" % (file,msg))
    if fileCnt == 0: logger.info("[%s]远程目录无文件可下载" % delivery["source"]["root_dir"])

def do_task():
    global taskId
    task = Tasks[taskId]
    ftp,msg = open_ftp(task["delivery"]["source"]["host"])
    if not ftp:
        logging.error("ftp连接失败,失败原因:%s,请检查FtpInfo[%d]配置" % (msg,taskId))
        return
    do_delivery(task["delivery"], ftp)
    ftp.close()

# 初始化
try:
    status,msg = checkTask()
    if not status:
        logger.error("程序初始化失败,失败原因:%s" % msg)
        exit()
    # 信号
    signo_quit = 0
    def on_signal(signo, stackframe):
        global signo_quit
        signo_quit = signo
    signames = {value: name for name, value in signal.__dict__.items() if
                name.startswith('SIG') and not name.startswith('SIG_')}
    signal.signal(signal.SIGTERM, on_signal)

    db = ftp_db.FTP_DBMS()
except Exception as e:
    logger.error('程序初始化失败,失败原因:%s' % traceback.format_exc())
    exit()

logger.info("Process startup ...")
while not signo_quit:
    try:
        if db.closed:
           db.connect()
        t1 = time.time()
        do_task()
        t2 = time.time()
        seconds = Tasks[taskId]["interval"] - (t2-t1)
        if seconds > 0: time.sleep(seconds)
    except pymysql.Error:
        logger.exception('mysql exception happend')
        db.close()
        time.sleep(20)
    except Exception as e:
        logger.error(traceback.format_exc())
        break

if signo_quit:
    logger.info('catch signal %s' % signames[signo_quit])
logger.info('Process exit')
