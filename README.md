# Syco-Signer

Tool used for daily syslog reviews.
  
Rsyslogd are configured to store all logs in the mysql table 
Syslog.SystemEvents. Preferable it's also configured to store all logs on 
another place, for example in the file system. This due to the fact that 
syco-signer will delete not wanted logs from mysql.

The user will then log into Syco-signer once a day, and see all yesterdays logs.
All log entries should then be reviewed for errors, security issues etc. When 
all logs are acceptable the user should sign that days logs with his login.

To reduce the number of logs it's possible to add triggers for none error logs
that will be deleted.

## Requirements

* Apache webserver
* Mysql database with logs
* Syslog standard logformat in syslog

Easiest is to install all requirements with bin/setup-syco and 
bin/setup-syco-signer. 


DESCRIPTION OF TABLES
=====================

signed - A row for each day that has been signed
------------------------------------------------

        id       - An autoincrement id
        sign     - Who did sign the logs.
        message  - A message/comment about this days logs.
        signdate - The date the logs where created.
        created  - The date the logs where signed, and this row was created.


trigger - A row for each message filter that should be handled
--------------------------------------------------------------


SystemEvents - Updated by rsyslogd
-----------------------------------


SystemEventsProperties - Updated by rsyslogd
--------------------------------------------