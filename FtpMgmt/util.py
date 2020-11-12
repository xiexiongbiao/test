import logging, logging.handlers
import os, os.path

def mysql_connect(db_login):
    import pymysql
    global mysqlDb_login
    conn = pymysql.connect(db_login['host'], db_login['user'],db_login['password'],db_login['db_name'],db_login['port'],charset='utf8' )
    return conn

def logger(name, fmt=None, when='D', backupCount=72, level_detail=None, level_error=None, level_console=None,
           passive=False,LOG_PATH="./"):
    if not fmt: fmt = '[%(asctime)s]<%(process)d:%(filename)s:%(lineno)d>%(levelname)s - %(message)s'
    if not os.path.exists(LOG_PATH): os.mkdir(LOG_PATH)
    formatter = logging.Formatter(fmt)
    logger = logging.getLogger(name)
    if passive: return logger
    logger.setLevel(logging.DEBUG)

    if level_detail:
        fh_detail = logging.handlers.TimedRotatingFileHandler(LOG_PATH + name + '.detail.log', when=when,
                                                              backupCount=backupCount)
        fh_detail.setLevel(level_detail)
        fh_detail.setFormatter(formatter)
        logger.addHandler(fh_detail)

    if level_error:
        fh_error = logging.handlers.TimedRotatingFileHandler(LOG_PATH + name + '.error.log', when=when,
                                                             backupCount=backupCount)
        fh_error.setLevel(level_error)
        fh_error.setFormatter(formatter)
        logger.addHandler(fh_error)

    if level_console:
        console = logging.StreamHandler()
        console.setLevel(level_console)
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger