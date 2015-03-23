EPIC
====
* setup-syco-signer
    * setup-database.py - Needs commandline parameters for questions.
    * Lite spridda lösenord som ska in i config fil.
    * load testdata data-signer.sql och data-systemevents.sql. Ej känslig
      info i dessa.
* syco-signer    
    * Lite spridda lösenord som ska in i config fil, verifiera att de används
      ifrån config fil.
    
* Add filter/search feature
* Add more triggers

TODO
====

https://docs.python.org/2/distutils/builtdist.html#creating-rpm-packages

syco-signer
* Counter in log-signer don't work. distinct is a bit strange

* Start testing cron_trigger.py and add real triggers.    
* Nagios script for warnings and alerts.
* Clean logs before inserted into mysql.
* Create cron.d file
* Create/Update install script.

* Fix the readme
* Dashboard with statisicts
    Signed most: mathem (240)
    Number of trigger deleted entries.
* Visas upp som en slags sammanfattning av alla triggers?

* Add https to vhost.conf, atleast selfsigned cert.
* Redirect http to https.
* Make a pip package with setup.py
* Create RPM package?
      
* Dump data from prod server
  
  mysqldump --tables myTable --where="id < 1000"
  mysqldump -u root -p Syslog SystemEvents --where "DeviceReportedTime between '2015-02-20 00:00' and '2014-10-22 12:00'" --no-create-info > systemevents.sql

* EFF vill kunna se sina loggar, särskild login till dom?

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
