#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Syco Signer
    ~~~~~~~~~~~

    :author: Daniel Lindh <daniel@cybercow.se>
    :copyright: (c) 2014 System Console project
    :license: see LICENSE for more details.
"""

import sys
import subprocess
import os.path

from sqlalchemy import create_engine


#
# Config
#

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'secret'
CON_NO_DATABASE = "mysql+mysqlconnector://root:secret@127.0.0.1/?charset=utf8"
CON_DATABASE = "mysql+mysqlconnector://root:secret@127.0.0.1/syslog?charset=utf8"


#
# Defines
#

ROOT_PATH = os.path.abspath(os.path.dirname(__file__) + '/../')
SQL_PATH = '{0}/var/sql'.format(ROOT_PATH)


#
# Helper/Utils functions
#

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " \
                             "(or 'y' or 'n').\n")


class DB():
    """Holder for a database engine and connection"""
    conf = None
    engine = None
    con = None

    def __init__(self, conf):
        self.conf = conf

    def __enter__(self):
        self.engine = create_engine(
            self.conf,
            convert_unicode=True, pool_size=50, pool_recycle=3600
        )
        self.con = self.engine.connect()
        return self.con

    def __exit__(self, type, value, traceback):
        self.con.close()


#
# Check and ask user what should be installed
#


def ask_create_database(con):
    result = con.execute('SHOW DATABASES LIKE "syslog"')
    if result.rowcount and 'syslog' in result.fetchone()[0]:
        print "* The database syslog already exist."
        if not query_yes_no("  Do you like to recreate the database?", "no"):
            return False
    return True


def ask_create_systemevents(con):
    result = con.execute('SHOW TABLES LIKE "SystemEvents"')
    if result.rowcount and 'SystemEvents' in result.fetchone()[0]:
        print "* The SystemEvents table already exist."
        if not query_yes_no("  Do you like to recreate the tables?", "no"):
            return False
    return True


def ask_create_log_viewer(con):
    result = con.execute('SHOW TABLES LIKE "signed"')
    if result.rowcount and 'signed' in result.fetchone()[0]:
        print "* The Syco Signer tables already exist."
        if not query_yes_no("  Do you like to recreate the tables?", "no"):
            return False
    return True


def ask_load(table):
    if not query_yes_no("* Do you like to load data in %s?" % table, "no"):
        return False
    else:
        return True


#
# Create database/tables
#


# TODO Backup database first.
#def backup_database():
#    BACKUP_FILE="/tmp/db-${YMDT}.sql.gz"
#    mysqldump -u${MYSQL_ROOT_USERNAME} -p${MYSQL_ROOT_PASSWORD} syslog | gzip -9 > ${BACKUP_FILE}


def mysql_load(filename):
    """Load an .sql file into mysql.

    This functions is a bit unsafe, it exposes the password for users
    that run top on another linus shell.
    """
    fn = os.path.join(SQL_PATH, filename)
    if not os.path.exists(fn):
        raise IOError("Can't find file {0}".format(fn))

    print '* Load file {0: <70}'.format(filename),
    sys.stdout.flush()
    if subprocess.call(
                    'mysql -u %s -p"%s" < %s' % (
                    MYSQL_USER, MYSQL_PASSWORD, fn
            ), shell=True
    ) == 1:
        raise RuntimeError("ERROR: Can't load %s" % filename)

    print '[ OK ]'


#
# Main
#


print "This script will recreate the mysql database table structure."
print
print "WARNING: All data in the database might be deleted."
print
with DB(CON_NO_DATABASE) as con:
    create_database = ask_create_database(con)

if create_database:
    create_systemevents = True
    create_log_viewer = True
else:
    with DB(CON_DATABASE) as con:
        create_systemevents = ask_create_systemevents(con)
        create_log_viewer = ask_create_log_viewer(con)

load_system_events = ask_load('SystemEvents')
load_log_viewer = ask_load('log-viewer')


#
# Do the database installation.
#

if create_database:
    mysql_load('create-database.sql')

if create_systemevents:
    mysql_load('create-systemevents.sql')

if create_log_viewer:
    mysql_load('create-signer.sql')

# TODO Cleanup ?
#if load_system_events:
#    mysql_load('data-systemevents.sql')

#if load_log_viewer:
#    mysql_load('data-signer.sql')

print "Done"
