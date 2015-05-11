# -*- coding: utf-8 -*-
#!/usr/local/pythonenv/syco-signer/bin/python
"""
    Syco Signer
    ~~~~~~~~~~~~~~

    :author: Daniel Lindh <daniel@cybercow.se>
    :copyright: (c) 2014 System Console project
    :license: see LICENSE for more details.

"""

import os.path

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from flask import Flask, request, g, redirect, url_for, render_template
from flask import flash
from flask.ext.login import login_required
from pylukinlib.flask.blueprint import login

import db
from util import signer_config, rest_response


# Create the application
app = Flask(__name__)
# WSGI requires this object.
application = app


# Default configurations that will/should be overridden by signer.cfg
app.config.update(dict(
    CON_DATABASE="mysql+mysqlconnector://user:password@127.0.0.1/Syslog?charset=utf8",
    DEBUG=False,
    SECRET_KEY='set-to-something-unique'
))

cnf = signer_config('signer.cfg', os.path.dirname(os.path.abspath(__file__)))
app.config.from_object(cnf)


# Create mysql connection
engine = create_engine(
    app.config['CON_DATABASE'],
    convert_unicode=True, pool_size=50, pool_recycle=3600
)


login.init_app(app, "dashboard", cnf.USERS)
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

def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)


#
# DASHBOARD VIEW
#

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


#
# SIGNED VIEW
#


@app.route('/signed')
@login_required
def signed():
    return render_template('signed.html')


@app.route('/signed.json')
@login_required
def signed_json():
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 10)
    sort = request.args.get('sort', "signdate")
    order = request.args.get('order', "desc")
    search = request.args.get('search', "")

    entries = db.signed(offset, limit, sort, order, search)
    return rest_response(entries)


#
# LOG-ENTRIES VIEW
#

@app.route('/log-entries/')
@login_required
def log_entries():
    return ''


@app.route('/log-entries/<date>')
@login_required
def log_entries_date(date):
    return render_template(
        'log-entries.html', date=date, signed=db.log_entries_signed(date)
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

    entries = db.log_entries(
        date, offset, limit, sort, order, search,
        from_host, sys_log_tag, message, distinct
    )
    return rest_response(entries)


@app.route('/log-entries/<date>', methods=['POST'])
@login_required
def add_entry(date):
    try:
        db.add_entry(current_user.username, request.form['sign_message'], date)
        return redirect(url_for('signed'))
    except IntegrityError:
        flash('New entry failed, duplicate entry.', 'flash-error')
    except Exception as e:
        flash('New entry failed.', 'flash-error')

    return redirect(url_for('log_entries', date=date))


#
# TRIGGER VIEW
#


@app.route('/trigger')
@login_required
def trigger():
    return render_template('trigger.html')


@app.route('/trigger.json')
@login_required
def trigger_json():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    sort = request.args.get('sort', "id")
    order = request.args.get('order', "desc")
    search = request.args.get('search', "")

    entries = db.triggers(offset, limit, sort, order, search)
    return rest_response(entries)


@app.route('/trigger/add')
@login_required
def trigger_add():
    return render_template('trigger-add.html', entry={})


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
    return render_template('trigger-add.html', entry=entries)


@app.route('/trigger/add', methods=['POST'])
@login_required
def trigger_add_save():
    entry = {
        'user': current_user.username,
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
    return render_template('trigger-edit.html', entry=db.trigger(id))


@app.route('/trigger/edit/<int:id>', methods=['POST'])
@login_required
def trigger_edit_save(id):
    try:
        entry = db.trigger(id)
        entry.update({
            'id': id,
            'user': current_user.username,
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
        db.trigger_delete(id)
        return rest_response()
    except Exception as e:
        return rest_response({}, status_code = 404)


#
# MAIN
#


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
