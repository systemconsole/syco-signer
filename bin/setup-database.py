#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Syco Signer Setup Database

:author: Daniel Lindh <daniel@cybercow.se>
:copyright: (c) 2014 System Console project
:license: see LICENSE for more details.
"""

import sys
import subprocess
import os.path
from optparse import OptionParser
from sqlalchemy import create_engine

sys.path.insert(0, '../')
from signer.util import signer_config


#
# Config
#


cnf = signer_config('signer.cfg', os.path.abspath('../signer/'))


#
# Defines
#

ROOT_PATH = os.path.abspath(os.path.dirname(__file__) + '/../')
SQL_PATH = '{0}/var/sql'.format(ROOT_PATH)


#
# Helper/Utils functions
#


def query_yes_no(question, default=True):
    """Ask a yes/no question via raw_input() and return their answer.

    question -- a string that is presented to the user.
    default  -- the presumed answer if the user just hits <Enter>.
                It must be True (yes), False or None (meaning
                an answer is required of the user).

    returns: True or False.
    todo: Move to lib?
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False,
             True: True, False: False}
    if default is None:
        prompt = " [y/n] "
    elif valid[default]:
        prompt = " [Y/n] "
    elif valid[default] is False:
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
            sys.stdout.write(
                "Please respond with 'yes' or 'no' (or 'y' or 'n').\n"
            )


class DB():
    """Holder for a database engine and connection

    Example:
        with DB(CON_DATABASE) as con:
            result = con.execute('SHOW TABLES LIKE "SystemEvents"')
    """
    conf = None
    engine = None
    con = None

    def __init__(self, conf):
        self.conf = conf

    def __enter__(self):
        self.engine = create_engine(
            self.conf, convert_unicode=True, pool_size=50, pool_recycle=3600
        )
        self.con = self.engine.connect()
        return self.con

    def __exit__(self, type, value, traceback):
        self.con.close()


#
# Check and ask user what should be installed
#


def ask_create_database(con):
    result = con.execute('SHOW DATABASES LIKE "Syslog"')
    if result.rowcount and 'Syslog' in result.fetchone()[0]:
        print "* The database Syslog already exist."
        return query_yes_no("  Do you like to recreate the database?", False)
    return True


def ask_create_systemevents(con):
    result = con.execute('SHOW TABLES LIKE "SystemEvents"')
    if result.rowcount and 'SystemEvents' in result.fetchone()[0]:
        print "* The SystemEvents table already exist."
        return query_yes_no("  Do you like to recreate the tables?", False)
    return True


def ask_create_log_signer(con):
    result = con.execute('SHOW TABLES LIKE "signed"')
    if result.rowcount and 'signed' in result.fetchone()[0]:
        print "* The Syco Signer tables already exist."
        return query_yes_no("  Do you like to recreate the tables?", False)
    return True


#
# Create database/tables
#


# TODO Backup database first.
# def backup_database():
#    BACKUP_FILE="/tmp/db-${YMDT}.sql.gz"
#    mysqldump -u${MYSQL_ROOT_USERNAME} -p${MYSQL_ROOT_PASSWORD} Syslog | gzip -9 > ${BACKUP_FILE}


def mysql_load(filename):
    """Load an .sql file into mysql.

    This functions is a bit unsafe, it exposes the password for users
    that run top on another linux shell.
    """
    fn = os.path.join(SQL_PATH, filename)
    if not os.path.exists(fn):
        raise IOError("Can't find file {0}".format(fn))

    print '* Load file {0: <70}'.format(filename),
    sys.stdout.flush()
    cmd = 'mysql -u %s -p"%s" < %s' % (cnf.DB_USER, cnf.DB_PASSWORD, fn)
    if subprocess.call(cmd, shell=True) == 1:
        raise RuntimeError("ERROR: Can't load %s" % filename)

    print '[ OK ]'


#
# Main
#


parser = OptionParser(
    description='Setup the syco-signer mysql database.',
    epilog='WARNING: All data in the database might be deleted.'
)
parser.add_option(
    "-f", "--force", action="store_true", default=False,
    help='Force recreate'
)

parser.add_option(
    "-d", "--data", action="store_true", default=False,
    help='Force load of data'
)

(options, args) = parser.parse_args()
print parser.description
print
print parser.epilog
print

with DB(cnf.CON_NO_DATABASE) as con_no_database:
    with DB(cnf.CON_DATABASE) as con_database:
        if options.force or ask_create_database(con_no_database):
            mysql_load('create-database.sql')

        if options.force or ask_create_systemevents(con_database):
            mysql_load('create-systemevents.sql')
            if options.data:
                mysql_load('create-systemevents-data.sql')

        if options.force or ask_create_log_signer(con_database):
            mysql_load('create-signer.sql')
            if options.data:
                mysql_load('create-signer-data.sql')

print "Done"
