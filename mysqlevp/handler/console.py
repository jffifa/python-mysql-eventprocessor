from __future__ import print_function, absolute_import, unicode_literals

import json
from .base import IEventHandler
from datetime import datetime
from pytz import timezone
from ..event.row_wrapper import InsertEventRow, UpdateEventRow, DeleteEventRow
from ..utils.time import naive_dt2str


class MysqlEvConsoleHandler(IEventHandler):
    def __init__(self, ev_tz='Asia/Shanghai', dt_col_tz='Asia/Shanghai', indent=4):
        """
        :param ev_tz: timezone for serializing the event timestamp
        :param dt_col_tz: TIMESTAMP and DATETIME columns in MySQL also gives a naive datetime object,
                          timezone info is also need for serializing
        :param indent: json dump indent
        """
        self.ev_tz = timezone(ev_tz)
        self.dt_col_tz = timezone(dt_col_tz)
        self.indent = indent

    def to_dict(self, ev_id, ev_timestamp, schema, table, row):
        res = {
            'ev_id':ev_id,
            'ev_time':str(datetime.fromtimestamp(ev_timestamp, self.ev_tz)),
            'schema':schema,
            'table':table,
        }
        if isinstance(row, InsertEventRow):
            res['new_values'] = naive_dt2str(row.new_values, self.dt_col_tz)
        elif isinstance(row, UpdateEventRow):
            res['old_values'] = naive_dt2str(row.new_values, self.dt_col_tz)
            res['new_values'] = naive_dt2str(row.new_values, self.dt_col_tz)
        elif isinstance(row, DeleteEventRow):
            res['old_values'] = naive_dt2str(row.old_values, self.dt_col_tz)
        else:
            raise NotImplementedError

        return res

    def dump(self, ev_id, ev_timestamp, schema, table, affected_rows):
        for row in affected_rows:
            print(json.dumps(
                    self.to_dict(ev_id, ev_timestamp, schema, table, row),
                    indent=self.indent,
            ))

    def on_insert(self, ev_id, ev_timestamp, schema, table, affected_rows):
        self.dump(ev_id, ev_timestamp, schema, table, affected_rows)

    def on_update(self, ev_id, ev_timestamp, schema, table, affected_rows):
        self.dump(ev_id, ev_timestamp, schema, table, affected_rows)

    def on_delete(self, ev_id, ev_timestamp, schema, table, affected_rows):
        self.dump(ev_id, ev_timestamp, schema, table, affected_rows)
