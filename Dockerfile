FROM python:3.5-alpine

# Install pymysql
COPY PyMySQL-0.9.3-py2.py3-none-any.whl /tmp
RUN pip3 install /tmp/PyMySQL-0.9.3-py2.py3-none-any.whl

# Install FtpMgmt
COPY FtpMgmt/ /root/FtpMgmt

WORKDIR /root/FtpMgmt

ENTRYPOINT ["/bin/sh", "-c", "sh start.sh"]