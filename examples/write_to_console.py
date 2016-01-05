from mysqlevp.handler.console import MysqlEvConsoleHandler
from mysqlevp.daemon import MysqlevpWrapper

table_filters = {
    'tr':['a'], # only receive events for TABLE "a" in DATABASE "tr"
}

hdlr = MysqlEvConsoleHandler()
mysql_conn_settings = {
    'host':'127.0.0.1',
    'port':3306,
    'user':'root',
    'passwd':'password',
}
mysqlevp = MysqlevpWrapper(
    mysql_conn_settings=mysql_conn_settings,
    replication_server_id=10,
    event_handler=hdlr,
    dump_file_path='/tmp/mysqlevp.dmp',
    table_filters=table_filters)
mysqlevp.run()
