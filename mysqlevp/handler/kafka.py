from __future__ import print_function, absolute_import, unicode_literals

import six
import json
from .base import IEventHandler
from datetime import datetime
from pytz import timezone
from ..event.row_wrapper import InsertEventRow, UpdateEventRow, DeleteEventRow
from ..utils.time import naive_dt2str
from kafka import KafkaClient, SimpleProducer


class MysqlEvKafkaHandler(IEventHandler):
    def __init__(self, ev_tz='Asia/Shanghai', dt_col_tz='Asia/Shanghai',
                 hosts=None, kafka_producer=None, topic=b'mysqlevp', split_row=False):
        """

        :param ev_tz: timezone for serializing the event timestamp
        :param dt_col_tz: TIMESTAMP and DATETIME columns in MySQL also gives a naive datetime object,
                          timezone info is also need for serializing
        :param hosts: lists of kafka hosts like
                      ["127.0.0.2:9092", "127.0.0.3:9092"]
        :param kafka_producer: if you want to control kafka producer more precisely,
                               you may give a kafka producer here,
                               if not given, a sync simple producer will be created with hosts param
                               be CAUTIOUS about using async mode for kafka producer as
                               the messages in its async sending queue may be LOST
                               if signal SIGKILL received.
        :param topic: the kafka topic messages sent to,
                      a string or a function,
                      if a function given, the function must receive 2 params(schema, table) and return a string
        :param split_row: if set to True, handler will split affected rows into messages,
                          each message contains only one row with "msg_key":"<ev_id>#<row_index>"
                          otherwise, handler just send one message for one event containing all affected rows,
                          each message has the key "ev_id":"<ev_id>" with "affected_rows[]"
        """
        if kafka_producer:
            self.kafka_producer = kafka_producer
        elif isinstance(hosts, list):
            host_str = ','.join(hosts)
            self.kafka_producer = SimpleProducer(
                KafkaClient(host_str),
                async=False,
                req_acks=SimpleProducer.ACK_AFTER_CLUSTER_COMMIT,
                ack_timeout=2000,
            )
        else:
            raise Exception('Invalid args for create kafka handler instance')

        if isinstance(topic, six.string_types):
            self.static_topic = topic
        elif callable(topic):
            self.static_topic = None
            self.topic_func = topic

        self.split_row = split_row
        self.ev_tz = timezone(ev_tz)
        self.dt_col_tz = timezone(dt_col_tz)

    @classmethod
    def gen_msg_key(cls, ev_id, row_index=None):
        if row_index:
            return six.b('#'.join([ev_id, str(row_index)]))
        else:
            return six.b(ev_id)

    def to_dict(self, ev_id, ev_timestamp, schema, table, row, msg_key=None):
        res = {
            'ev_id':ev_id,
            'ev_time':str(datetime.fromtimestamp(ev_timestamp, self.ev_tz)),
            'schema':schema,
            'table':table,
        }
        if msg_key:
            res['msg_key'] = msg_key

        if isinstance(row, InsertEventRow):
            res['action'] = 'INSERT'
            res['new_values'] = naive_dt2str(row.new_values, self.dt_col_tz)
        elif isinstance(row, UpdateEventRow):
            res['action'] = 'UPDATE'
            res['old_values'] = naive_dt2str(row.new_values, self.dt_col_tz)
            res['new_values'] = naive_dt2str(row.new_values, self.dt_col_tz)
        elif isinstance(row, DeleteEventRow):
            res['action'] = 'DELETE'
            res['old_values'] = naive_dt2str(row.old_values, self.dt_col_tz)
        else:
            raise NotImplementedError

        return res

    def send_msgs(self, ev_id, ev_timestamp, schema, table, affected_rows):
        topic = six.b(self.static_topic or self.topic_func(schema=schema, table=table))

        if self.split_row:
            msg_list = []
            for row_index, row in enumerate(affected_rows):
                msg = self.to_dict(ev_id, ev_timestamp, schema, table, row, self.gen_msg_key(ev_id, row_index))
                msg_list.append(six.b(json.dumps(msg)))

            self.kafka_producer.send_messages(topic, *msg_list)
        else:
            row_list = [self.to_dict(ev_id, ev_timestamp, schema, table, row) for row in affected_rows]
            msg_dict = {
                'ev_id':ev_id,
                'ev_time':str(datetime.fromtimestamp(ev_timestamp, self.ev_tz)),
                'schema':schema,
                'table':table,
                'affected_rows':row_list,
            }
            msg = six.b(json.dumps(msg_dict))
            self.kafka_producer.send_messages(topic, self.gen_msg_key(ev_id), msg)

    def on_insert(self, ev_id, ev_timestamp, schema, table, affected_rows):
        self.send_msgs(ev_id, ev_timestamp, schema, table, affected_rows)

    def on_update(self, ev_id, ev_timestamp, schema, table, affected_rows):
        self.send_msgs(ev_id, ev_timestamp, schema, table, affected_rows)

    def on_delete(self, ev_id, ev_timestamp, schema, table, affected_rows):
        self.send_msgs(ev_id, ev_timestamp, schema, table, affected_rows)


