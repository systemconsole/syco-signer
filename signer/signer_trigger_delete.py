#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Syco Signer Trigger Delete
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Remove rows from table SystemEvents in the mysql database Syslog
    that matches the regexps in the table trigger.

    :author: Daniel Lindh <daniel@cybercow.se>
    :copyright: (c) 2014 System Console project
    :license: see LICENSE for more details.

"""

from datetime import date, timedelta, datetime, time
from sqlalchemy.sql.expression import text
from sqlalchemy import create_engine
import os

from util import config, logger, only_allow_one_instance

triggers_sql = text("""
SELECT
    id,
    from_host_trigger,
    sys_log_tag_trigger,
    message_trigger
FROM
    `trigger`
WHERE
    status = 'DELETE'
""")


def triggers(con):
    """Yield all DELETE triggers."""
    result = con.execute(triggers_sql)
    for row in result:
        yield row
    result.close()


clean_system_events_sql = text("""
DELETE
FROM
    SystemEvents
WHERE
    SystemEvents.FromHost LIKE :from_host AND
    SystemEvents.SysLogTag LIKE :sys_log_tag AND
    SystemEvents.Message LIKE :message AND
    SystemEvents.DeviceReportedTime BETWEEN :yesterday AND :today
""")


def clean_system_events(from_host, sys_log_tag, message):
    """Delete SystemEvents matching regexp args."""
    result = con.execute(
        clean_system_events_sql,
        from_host=from_host, sys_log_tag=sys_log_tag, message=message,
        yesterday=datetime.combine(date.today() - timedelta(1), time(0, 0)),
        today=datetime.combine(date.today(), time(23, 59))
    )
    num = result.rowcount
    result.close()
    return num


update_trigger_with_delete_stats_sql = text("""
UPDATE `trigger`
SET
    total_deleted=total_deleted+:matched,
    deleted_since_changed=deleted_since_changed+:matched,
    last_delete=NOW()
WHERE
    id = :id
""")


def update_trigger_with_delete_stats(id, num_of_rows):
    """Trigger table with delete statistics"""
    result = con.execute(
        update_trigger_with_delete_stats_sql, id=id, matched=num_of_rows
    )
    result.close()


def clean_mysql(con):
    """Remove SystemEvents matching regexps in trigger table"""
    total = 0
    for id, from_host, sys_log_tag, message in triggers(con):
        num_of_rows = clean_system_events(from_host, sys_log_tag, message)
        update_trigger_with_delete_stats(id, num_of_rows)
        total += num_of_rows
    logger('Deleted %s SystemEvents matched by triggers.' % total)


#
# Main
#


if __name__ == "__main__":
    only_allow_one_instance('signer_trigger_clean.pid')

    cnf = config('signer.cfg', os.path.dirname(os.path.abspath(__file__)))
    engine = create_engine(
        cnf.DATABASE,
        convert_unicode=True, pool_size=50, pool_recycle=3600
    )

    con = engine.connect()
    clean_mysql(con)
    con.close()