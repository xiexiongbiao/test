import pymysql
import config

sql_add_Fileinfo = "insert into ftp_file_info (file_name,system_user,system_name,download_url,modify_time,create_time,file_size) VALUES(%s,%s,%s,%s,STR_TO_DATE(%s, '%%Y%%m%%d%%H%%i%%s'),sysdate(),%s)"

sql_select_Fileinfo = "select system_user,system_name,download_url from system_config_tbl where file_name_prefix = %s"

class FTP_DBMS:
    def __init__(self):
        self.closed = True
        self.connect()

    def connect(self):
        self.db = config.mysql_connect(config.db_login)
        self.closed = False

    def close(self):
        try:
            self.db.close()
        except:
            pass
        self.closed = True

    def checkConnect(self):
        try:
            c = self.db.cursor()
            c.execute("select 1")
        except pymysql.Error:
            self.close()
            self.connect()
        finally:
            c.close()

    def inserFileinfo(self,parse_res,file_modify_time,file_size,file):
        try:
            c = self.db.cursor()
            c.execute(sql_add_Fileinfo,(file,parse_res[0][0],parse_res[0][1],parse_res[0][2],file_modify_time,file_size))
            self.db.commit()
            c.close()
            return True,None
        except Exception as e:
            return False,str(e)

    def selectFileinfo(self,file_name_prefix):
        try:
            c = self.db.cursor()
            c.execute(sql_select_Fileinfo,(file_name_prefix,))
            rows = c.fetchall()
            c.close()
            if len(rows) == 0:
                return None,"system_config_tbl表找不到[%s]文件名前缀相关文件信息，请配置" % file_name_prefix
            if len(rows) >=2:
                return None, "[%s]文件名前缀在system_config_tbl查询出[%s]条记录，请检查配置" % (file_name_prefix,str(len(rows)))
            return rows,None
        except Exception as e:
            return None,str(e)