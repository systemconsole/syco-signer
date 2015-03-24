# The Syco Logviwer

## Requirements

* Install
    iptables -A FORWARD -p tcp -s 10.101.1.7 -m multiport --dports 80,443 -j allowed_tcp
    yum install python-pip wsgi_module  # Enable epel first /etc/yum.repos.d/epel.repo
    pip install mysql-connector-python
    pip install Flask-sqlalchemy
    chmod -R u=rw,g=r,o=r,u+X,g+X,o+X  /usr/lib/python2.6/site-packages/

* Install mysql
    GRANT select, update, delete, insert ON Syslog.* TO 'sycosigner'@'127.0.0.1' IDENTIFIED BY 'xxx';
    insert  into signed2(id, sign, message, signdate, created) select id, sign, mess, signdate, date from signed group by signdate;
    rename table signed to signedold;
    rename table signed2 to signed;
    delete from signed where id =361;
    drop table signedold;

* Apache webserver
* Mysql database with logs
* Syslog standard logformat in syslog
* Syco to generate host list for webpage

## Install

* Copy the www folder containing all www files to /var/www/html/
* Copy the apache vhost.conf file in the etc folder to /etc/httpd/cond.d
* Make sure that the mod_cgi.se is enabled in you apache config /etc/httpd/httpd.conf
* Setup user i htaccess file or use ldap read.
* Setup mysql settings in the mysql.py file (User must have read to Syslog database)
* Run sql file for mysql config

### SQL User

    GRANT SELECT,INSERT,UPDATE on Syslog.Exclude TO 'rsyslogd'@'localhost';
    GRANT SELECT,INSERT,UPDATE on Syslog.alert TO 'rsyslogd'@'localhost';
    GRANT SELECT,INSERT,UPDATE on Syslog.signed TO 'rsyslogd'@'localhost';
    GRANT SELECT on Syslog.* TO 'rsyslogd'@'localhost';

### Extra nagios monitoring

* Extra: Setup logclean script
* Extra: Use nagios to montor logs

* Setup in webpage what to exclude and alert in.
* "OK" settings will generate alerts if log entory is not find on the host chosen.

* Cleaning out none wanted log entries define with add this script to crontab to
run every hour. mysql_clean_exclude.py

* Nagios alert are triggered with nrpe to run on the script
auto_alert.py 

### Set up ldap to users
* Use ldap instead of htacess file to host files.
* Uncomment the ldap section in the vhost.conf file

## Use
* Show daily logs
* Signing of logs
* Hiding use logresults
* Removing non use log results
* Trigger nagios alert on logs fins i db
* Trigger nagios alert on log NOT find in db on host



DESCRIPTION OF TABLES
=====================

signed
------
id       - An autoincrement id
created  - The date the logs where signed, and this row was created.
signdate - The date the logs where created.
sign     - Who did sign the logs.
message  - A message/comment about this days logs.
