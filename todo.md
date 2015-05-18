EPIC
====

TODO
====

* Add https to vhost.conf, atleast selfsigned cert.
* Redirect http to https.


* Make a pip package with setup.py
* Create RPM package?
    https://docs.python.org/2/distutils/builtdist.html#creating-rpm-packages
* Use LDAP Accounts?
* Enable SELinux

* Start testing cron_trigger.py and add real triggers.    
* Nagios script for warnings and alerts.
* Clean logs before inserted into mysql.
* Create cron.d file


* Dashboard with statisicts
    Signed most: mathem (240)
    Number of trigger deleted entries.
* Visas upp som en slags sammanfattning av alla triggers?



* EFF vill kunna se sina loggar, särskild login till dom?

* SQL User
    GRANT select, update, delete, insert ON Syslog.* TO 'sycosigner'@'127.0.0.1' IDENTIFIED BY 'xxx';
    GRANT SELECT,INSERT,UPDATE on Syslog.Exclude TO 'rsyslogd'@'localhost';
    GRANT SELECT,INSERT,UPDATE on Syslog.alert TO 'rsyslogd'@'localhost';
    GRANT SELECT,INSERT,UPDATE on Syslog.signed TO 'rsyslogd'@'localhost';
    GRANT SELECT on Syslog.* TO 'rsyslogd'@'localhost';


Syco
====

Master password
    * https://github.com/systemconsole/syco/issues/128
    * Use master password in .syco.cnf if it exist. 
      /root/.syco.cnf
      master-password: xxxx
      
    * Move password file to it's own file.
    * Delete master password after 60 minutes with cronjob.
      Check file modify time to determine if 60 minuts has passed.
    * Switch in syco that keeps the password for another 60 minutes.
      -k --keep-password -- Do that by touching the file.

RPM
    * Rpm that install .syco.cnf and master-password cleaner.
      Or kickstart file that create the .syco.cnf file before installing lots
      of rpms.
    * Kan man lägga rpm:er på github och installera därifrån?
      Isåfall en syco-password.rpm där, med default password.
      Sedan att man lägger på en rpm ifrån sitt eget repo som överlagrar denna
      rpm.
    * Hur ska en rpm katalog se ut, bara http trafik dit?
    * Kan man överlagra rpmer, vad händer om samma rpm finns i flera repos.  
* Create centos VirtualBox image.
  https://github.com/INSANEWORKS/centos-packer
