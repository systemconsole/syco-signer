# -*- coding: utf-8 -*-
"""
    Database queries
    ~~~~~~~~~~~~~~~~

    :author: Daniel Lindh <daniel@cybercow.se>
    :copyright: (c) 2014 System Console project
    :license: see LICENSE for more details.

"""

from datetime import datetime, timedelta
from itertools import islice
from operator import itemgetter
from sqlalchemy.sql.expression import text
from flask import g


#
# SIGNED
#

def signed(offset, limit, sort, order, search):
    return {
        'total': signed_count(search),
        'rows': signed_result(int(offset), int(limit), sort, order, search),
    }


def signed_count(search):
    """Calculate number of signed days."""
    days = signed_result(None, None, None, None, search)
    return len(days)


def signed_result(offset, limit, sort, order, search):
    """Return a dict with all signed and unsigned days since first sign.

    days['2014-01-01'] = {'signdate': '2014-01-01', 'sign':... }

    """
    days = unsigned_days()
    cur = g.con.execute(text('SELECT * FROM signed ORDER BY id DESC '))
    for row in cur.fetchall():
        row = dict(row)
        row['signdate'] = row['signdate'].strftime('%Y-%m-%d')
        days.append(row)

    if sort is None and limit is None:
        return days
    else:
        reverse = True if order == 'asc' else False
        sorted_days = sorted(days, key=itemgetter(sort), reverse=reverse)
        return [x for x in islice(sorted_days, offset, offset+limit)]


def unsigned_days():
    """Return a dict with all days since first sign.

    Value is a default dict.

    days['2014-01-01'] = {'signdate': '2014-01-01'  }
    """
    cur = g.con.execute(
        'SELECT MIN(DeviceReportedTime) AS signdate FROM SystemEvents '
        'UNION '
        'SELECT MIN(signdate) AS signdate FROM signed '
        'ORDER BY signdate ASC limit 1'
    )
    first_sign_date = cur.fetchone()['signdate']

    if not first_sign_date:
        first_sign_date = datetime.now() - timedelta(1)
    first_sign_date = datetime.combine(first_sign_date, datetime.min.time())

    def _key(x):
        return (datetime.now() - timedelta(x)).strftime('%Y-%m-%d')

    days = (datetime.now() - first_sign_date).days + 1
    unsigned = []
    for x in xrange(days):
        unsigned.append({
            'signdate': _key(x),
            'sign': None,
            'created': None,
            'message': None
        })

    return unsigned


#
# LOG-ENTRIES
#


def log_entries(
    date, offset, limit, sort, order, search,
    from_host, sys_log_tag, message, distinct
):
    return {
        'total': log_entries_count(date, search, from_host, sys_log_tag, message, distinct),
        'rows': log_entries_result(
            date, offset, limit, sort, order, search,
            from_host, sys_log_tag, message, distinct
        ),
    }


def sql_log_entries_count(from_host, sys_log_tag, message, distinct):
    return text("""
SELECT
  count(*) as log_entries
FROM
    (
        SELECT
            FromHost, SysLogTag, Message
        FROM
            SystemEvents
        WHERE
            DeviceReportedTime BETWEEN :from_date AND :to_date """ +
            sql_log_entries_where(from_host, sys_log_tag, message) +
            sql_log_entries_group_by(distinct) + """
    ) s1;
""")


def sql_log_entries_result(from_host, sys_log_tag, message, distinct, sort, order):
    return text("""
SELECT
    *,
    count(ID) as counter
FROM
    SystemEvents
Where
    DeviceReportedTime BETWEEN :from_date AND :to_date """ +
    sql_log_entries_where(from_host, sys_log_tag, message) +
    sql_log_entries_group_by(distinct) + """
ORDER BY
    {sort} {order}
LIMIT
    :offset, :limit
""".format(sort=sort, order=order))


def sql_log_entries_where(from_host, sys_log_tag, message):
    where = ''
    if from_host:
        where += 'AND FromHost like :from_host '

    if sys_log_tag:
        where += 'AND SysLogTag like :sys_log_tag '

    if message:
        where += 'AND Message like :message '

    return where


def sql_log_entries_group_by(distinct):
    if distinct:
        return 'GROUP BY FromHost, Message '
    else:
        return 'GROUP BY ID '


def log_entries_count(date, search, from_host, sys_log_tag, message, distinct):
    """Calculate number of log_entries."""
    day = datetime.strptime(date, '%Y-%m-%d')

    cur = g.con.execute(
        sql_log_entries_count(from_host, sys_log_tag, message, distinct),
        from_date=day.strftime('%Y-%m-%d 00:00:00'),
        to_date=day.strftime('%Y-%m-%d 23:59:59'),
        from_host=from_host,
        sys_log_tag=sys_log_tag,
        message=message
    )
    num = cur.fetchone()['log_entries']
    cur.close()
    return num


def log_entries_result(
    date, offset, limit, sort, order, search,
    from_host, sys_log_tag, message, distinct
):
    def format_row(row):
        row = dict(row)
        row['ReceivedAt'] = row['ReceivedAt'].strftime('%Y-%m-%d %H:%M:%S')
        row['DeviceReportedTime'] = row['DeviceReportedTime'].strftime('%Y-%m-%d %H:%M:%S')
        return row

    day = datetime.strptime(date, '%Y-%m-%d')
    sql=sql_log_entries_result(from_host, sys_log_tag, message, distinct, sort, order)
    cur = g.con.execute(
        sql,
        from_date=day.strftime('%Y-%m-%d 00:00:00'),
        to_date=day.strftime('%Y-%m-%d 23:59:59'),
        offset=offset,
        limit=limit,
        sort=sort,
        order=order,
        from_host=from_host,
        sys_log_tag=sys_log_tag,
        message=message
    )
    entries = [format_row(row) for row in cur.fetchall()]
    cur.close()
    return entries


sql_log_entries_signed = text("""
SELECT
    id, sign, message, signdate, created
FROM
    signed
WHERE
    signdate = :signdate
""")


def log_entries_signed(signdate):
    cur = g.con.execute(sql_log_entries_signed, signdate=signdate)
    result = cur.fetchone()
    cur.close()
    return result


add_entry_sql = text("""
REPLACE INTO signed (
    sign,
    message,
    signdate,
    created
)
VALUES (
    :sign,
    :message,
    :signdate,
    NOW()
)
""")


def add_entry(sign, message, date):
    g.con.execute(add_entry_sql, sign=sign, message=message, signdate=date)


#
# TRIGGERS
#


def triggers(offset, limit, sort, order, search):
    return {
        'total': triggers_count(search),
        'rows': triggers_result(offset, limit, sort, order, search),
    }


sql_triggers_count = text("""
SELECT
    count(*) as triggers
FROM
    `trigger`
""")


def sql_triggers_result(sort, order):
    return text("""
SELECT
    *
FROM
    `trigger`
ORDER BY
    {sort} {order}
LIMIT
    :offset, :limit
""".format(sort=sort, order=order))


def triggers_count(search):
    """Calculate number of triggers."""
    cur = g.con.execute(sql_triggers_count)
    num = cur.fetchone()['triggers']
    cur.close()
    return num


def triggers_result(offset, limit, sort, order, search):
    def format_row(row):
        row = dict(row)
        row['created'] = row['created'].strftime('%Y-%m-%d %H:%M:%S')
        row['changed'] = row['changed'].strftime('%Y-%m-%d %H:%M:%S') if row['changed'] else None
        return row

    cur = g.con.execute(
        sql_triggers_result(sort, order),
        offset=offset, limit=limit, sort=sort, order=order
    )
    entries = [format_row(row) for row in cur.fetchall()]
    cur.close()
    return entries


def system_event(systemevent_id):
    cur = g.con.execute(
        text(
            'SELECT * FROM SystemEvents '
            'WHERE ID = :id'
        ),
        id=systemevent_id
    )
    entries = cur.first()
    cur.close()
    return entries


trigger_sql = text("""
SELECT
  *
FROM
    `trigger`
WHERE
    id = :id
""")


def trigger(id):
    cur = g.con.execute(trigger_sql, id=id)
    entry = dict(cur.first())
    cur.close()
    return entry


trigger_insert_update_sql = text("""
INSERT INTO `trigger` (
    user,
    status,
    from_host_trigger,
    sys_log_tag_trigger,
    message_trigger,
    deleted_since_changed,
    created
)
VALUES (
    :user,
    :status,
    :from_host_trigger,
    :sys_log_tag_trigger,
    :message_trigger,
    0,
    NOW()
)
ON DUPLICATE KEY UPDATE
    user=:user,
    status=:status,
    from_host_trigger=:from_host_trigger,
    sys_log_tag_trigger=:sys_log_tag_trigger,
    message_trigger=:message_trigger,
    deleted_since_changed=0,
    changed=NOW()
""")


def trigger_insert_update(entries):
    g.con.execute(trigger_insert_update_sql, **entries)


trigger_update_sql = text("""
UPDATE
    `trigger`
SET
    user=:user,
    status=:status,
    from_host_trigger=:from_host_trigger,
    sys_log_tag_trigger=:sys_log_tag_trigger,
    message_trigger=:message_trigger,
    deleted_since_changed=0,
    changed=NOW()
WHERE
    `id` = :id
""")


def trigger_update(entries):
    g.con.execute(trigger_update_sql, **entries)


trigger_delete_sql = text("""
DELETE FROM
    `trigger`
WHERE
  id = :id
""")


def trigger_delete(id):
    g.con.execute(trigger_delete_sql, id=id)
