#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Syco Signer Helper Functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: Daniel Lindh <daniel@cybercow.se>
    :copyright: (c) 2014 System Console project
    :license: see LICENSE for more details.

"""

import os.path
import subprocess
import fcntl
import imp
import os.path
import errno
from flask.json import current_app, dumps, request
import sys


def signer_config(filename, root_path):
    """Config file loader for syco-signer"""
    cnf = config(filename, root_path)
    for name in ('CON_DATABASE', 'CON_NO_DATABASE', 'DB_USER', 'DB_PASSWORD', 'SECRET_KEY', 'USERS'):
        if not hasattr(cnf, name):
            raise KeyError('Missing parameter %s in config file.' % name)
    return cnf


def config(filename, root_path):
    """Get configuration options from file in /etc/ or root_path.

    Example:
    cnf = config('app.cfg', os.path.dirname(os.path.abspath(__file__)))
    create_engine(cnf.DATABASE)
    """
    cnf = _config('/etc/%s' % filename)
    if cnf is False:
        filename = os.path.join(root_path, filename)
        cnf = _config(filename)
    return cnf


def _config(full_path_filename):
    """Get configuration options from full path filename.

    Example:
    cnf = config('/etc/signer.cfg')
    create_engine(cnf.DATABASE)
    """
    d = imp.new_module('config')
    d.__file__ = full_path_filename
    try:
        with open(full_path_filename) as config_file:
            exec (compile(config_file.read(), full_path_filename, 'exec'), d.__dict__)
    except IOError as e:
        if e.errno in (errno.ENOENT, errno.EISDIR):
            return False
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return d


def logger(msg):
    """Logging to syslog.

    Example:
    logger("This will be added to syslog")
    """
    log_this = "logger -t syco-task -s '%s'" % msg
    subprocess.Popen(log_this.split())


# Need this global variable to keep the lock scope after the function exits.
only_allow_one_instance_fp = None
def only_allow_one_instance(pid_file):
    """Verify that only one instance of the script are running.

    Example:
    only_allow_one_instance('app.pid')
    """
    global only_allow_one_instance_fp
    only_allow_one_instance_fp = open('/tmp/pid.pid', 'w')
    try:
        fcntl.lockf(only_allow_one_instance_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another instance is running, exit!")
        sys.exit(1)


def jsonify_list(data):
    """Creates a JSON view response.

    This is a modified version of flask.helpers.jsonify, but this function
    takes an OrderedDict so the json file can be printed in proper order.

    It also decodes utf-8 characters.
    """
    assert data is not None
    indent = None
    if (current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and
            not request.is_xhr):
        indent = 2
    data = dumps(data, indent=indent, sort_keys=False)

    mimetype = 'application/json; charset=utf-8'
    response = current_app.response_class(data, mimetype=mimetype)

    return response

def rest_response(data, status_code = 200):
    response = jsonify_list(data)
    response.status_code = status_code
    return response