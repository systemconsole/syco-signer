TODO
====

* Counter in log-signer don't work. distinct is a bit strange



* Webres disable avahi-daemon. 
  This is a mDNS service. It's disabled on all centos 6 servers. The service
  sends out a lot of multicast messages.
  chkconfig avahi-daemon off
  /etc/init.d/avahi-daemon stop

* Need another solution than sending password on command line.
  COMMAND=/usr/lib64/nagios/plugins/check_ldap.php -H ldaps://ldap-tc.fareoffice.com:636 -U cn=sssd,dc=fareoffice,dc=com -P xxxx

* Eff gives lots of http errors
  http://10.101.1.7/syco-signer/trigger/edit/241  
  
* We have several "IPT: New not syn" errors from iptables. Is something wrong 
  with them? Or should they just be deleted with syco-signer from logs? Now
  a trigger deletes them.
  Ie:
  IN= OUT=eth1 SRC=10.101.1.97 DST=65.197.19.151 LEN=77 TOS=0x00 PREC=0x00 
  TTL=64 ID=843 DF PROTO=TCP SPT=42755 DPT=443 WINDOW=103 RES=0x00 ACK PSH URGP=0  
  
* Some minor DNS-settings
  http://www.dnsinspect.com/fareoffice.com/1413815168#mail
  
  
* Dump data from prod server
  
  mysqldump --tables myTable --where="id < 1000"
  mysqldump -u root -p Syslog SystemEvents --where "DeviceReportedTime between '2014-10-26 00:00' and '2014-10-26 12:00'" --no-create-info > systemevents.sql

* Start testing cron_trigger.py and add real triggers.    
* Nagios script for warnings and alerts.
* Clean logs before inserted into mysql.
* Create cron.d file
* Create/Update install script.
* Make a pip package with setup.py

* Fix the readme
* Dashboard with statisicts
    Signed most: mathem (240)
    Number of trigger deleted entries.
* Visas upp som en slags sammanfattning av alla triggers?

* Add https to vhost.conf, atleast selfsigned cert.
* Redirect http to https.
* Create RPM package?