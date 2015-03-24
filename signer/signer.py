# -*- coding: utf-8 -*-
#!/usr/local/pythonenv/syco-signer/bin/python
"""
    Syco Signer
    ~~~~~~~~~~~~~~

    :author: Daniel Lindh <daniel@cybercow.se>
    :copyright: (c) 2014 System Console project
    :license: see LICENSE for more details.

    DESCRIPTION OF TABLES
    =====================

    signed
    ------
    id       - An autoincrement id
    created  - The date the logs where signed, and this row was created.
    signdate - The date the logs where created.
    sign     - Who did sign the logs.
    message  - A message/comment about this days logs.

"""

from math import ceil
import sys
import os.path
from functools import wraps

from sqlalchemy import create_engine
from flask import Flask, request, g, redirect, url_for, render_template
from flask import flash, abort
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError

from pylukinlib.flask.blueprint import login

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import db
from util import config, jsonify_list, rest_response

# create our little application :)
app = Flask(__name__)
# WSGI requires this object.
application = app


# Default configurations that will/should be overridden in signer.cfg
app.config.update(dict(
    DATABASE="mysql+mysqlconnector://user:password@127.0.0.1/Syslog?charset=utf8",
    DEBUG=False,
    # Generate a new secret key everytime the wsgi are restarted. This
    # will invalidate all sessions between restarts.
    SECRET_KEY='i\xb0\x11S2\xbd_\xb7>\xd2{\xc6\xd0\xc5g\xcb\xd74\xedO\x07(~\x07'
))

cnf = config('signer.cfg', os.path.dirname(os.path.abspath(__file__)))
app.config.from_object(cnf)

# Number of rows displayed on one html page.
PER_PAGE = cnf.PER_PAGE

# Create mysql connection
engine = create_engine(
    app.config['DATABASE'],
    convert_unicode=True, pool_size=50, pool_recycle=3600
)

login.init_app(app, "dashboard", {"user": "password"})
app.register_blueprint(login.login_pages)


@app.before_request
def connect_db():
    """Create a connection to the database before each request."""
    if not hasattr(g, 'con'):
        g.con = engine.connect()


@app.teardown_request
def close_db(ex):
    """Close database connection after each request."""
    if hasattr(g, 'con'):
        g.con.close()
        delattr(g, 'con')


#
# UTILS
#

class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if (num <= left_edge or
                    (self.page - left_current - 1 < num <
                             self.page + right_current) or
                        num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def url_for_other_page(page):
    aa = request.args.copy()
    args = request.view_args.copy()
    args = dict(args.items() + aa.items())
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)


def remote_user():
    return request.environ.get('REMOTE_USER', 'Unknown')


#
# DASHBOARD
#

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', REMOTE_USER=remote_user())


#
# SIGNED
#


@app.route('/signed')
@login_required
def signed():
    return render_template('signed.html', REMOTE_USER=remote_user())


@app.route('/signed.json')
@login_required
def signed_json():
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 10)
    sort = request.args.get('sort', "signdate")
    order = request.args.get('order', "desc")
    search = request.args.get('search', "")

    entries = db.signed(offset, limit, sort, order, search)
    return jsonify_list(entries)


#
# LOG-ENTRIES
#


@app.route('/log-entries/<date>')
@login_required
def log_entries(date):
    return render_template(
        'log-entries.html', REMOTE_USER=remote_user(),
        date=date,
        signed=db.log_entries_signed(date)
    )


@app.route('/log-entries.json/<date>')
@login_required
def log_entries_json(date):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    sort = request.args.get('sort', "id")
    order = request.args.get('order', "desc")
    search = request.args.get('search', "")

    #
    from_host = request.args.get('from_host', "")
    sys_log_tag = request.args.get('sys_log_tag', "")
    message = request.args.get('message', "")
    distinct = True if request.args.get('distinct') == 'true' else False

    if app.config['DEBUG'] is True:
        date = '2014-10-26'

    entries = db.log_entries(
        date, offset, limit, sort, order, search,
        from_host, sys_log_tag, message, distinct
    )
    return jsonify_list(entries)


@app.route('/log-entries/<date>', methods=['POST'])
@login_required
def add_entry(date):
    try:
        db.add_entry(remote_user(), request.form['sign_message'], date)
        return redirect(url_for('signed'))
    except IntegrityError:
        flash('New entry failed, duplicate entry.', 'flash-error')
    except Exception as e:
        flash('New entry failed.', 'flash-error')

    return redirect(url_for('log_entries', date=date))


#
# TRIGGER
#


@app.route('/trigger')
@login_required
def trigger():
    return render_template(
        'trigger.html', REMOTE_USER=remote_user()
    )


@app.route('/trigger.json')
@login_required
def trigger_json():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    sort = request.args.get('sort', "id")
    order = request.args.get('order', "desc")
    search = request.args.get('search', "")

    entries = db.triggers(offset, limit, sort, order, search)
    return jsonify_list(entries)


@app.route('/trigger/add')
@login_required
def trigger_add():
    return render_template(
        'trigger-add.html', entry={}, REMOTE_USER=remote_user()
    )


@app.route('/trigger/add/<int:systemevents_id>')
@login_required
def trigger_add_system_event(systemevents_id):
    result = db.system_event(systemevents_id)
    entries = {
        'from_host_trigger': result['FromHost'],
        'sys_log_tag_trigger': result['SysLogTag'],
        'message_trigger': result['Message'],
        'back_url': redirect_url('trigger')
    }
    return render_template(
        'trigger-add.html', entry=entries, REMOTE_USER=remote_user()
    )


@app.route('/trigger/add', methods=['POST'])
@login_required
def trigger_add_save():
    entry = {
        'user': remote_user(),
        'status': request.form['inputStatus'],
        'from_host_trigger': request.form['inputFromHost'],
        'sys_log_tag_trigger': request.form['inputSysLogTag'],
        'message_trigger': request.form['inputMessage']
    }
    try:
        db.trigger_insert_update(entry)
        return redirect(request.form['inputBackUrl'])
    except Exception as e:
        flash('New entry failed.', 'flash-error')

    entry['back_url'] = request.form['inputBackUrl']
    return render_template('trigger-add.html', entry=entry)


@app.route('/trigger/edit/<int:id>')
@login_required
def trigger_edit(id):
    return render_template(
        'trigger-edit.html', entry=db.trigger(id), REMOTE_USER=remote_user()
    )


@app.route('/trigger/edit/<int:id>', methods=['POST'])
@login_required
def trigger_edit_save(id):
    try:
        entry = db.trigger(id)
        entry.update({
            'id': id,
            'user': remote_user(),
            'status': request.form['inputStatus'],
            'from_host_trigger': request.form['inputFromHost'],
            'sys_log_tag_trigger': request.form['inputSysLogTag'],
            'message_trigger': request.form['inputMessage']
        })

        # Need insert/update in case the trigger already exist.
        db.trigger_update(entry)
        return redirect(url_for('trigger'))
    except IntegrityError:
        flash('Duplicate entry, trigger already exist.', 'flash-error')
    except Exception as e:
        flash('New entry failed.', 'flash-error')

    return render_template('trigger-edit.html', entry=entry)


@app.route('/trigger/delete/<int:id>', methods=['POST'])
@login_required
def trigger_delete(id):
    try:
        #db.trigger_delete(id)
        return rest_response()
    except Exception as e:
        return rest_response({}, status_code = 200)


#
# MAIN
#


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
