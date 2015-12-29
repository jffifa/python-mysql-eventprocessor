# MySQL Event Processor

Daemon interface for handling MySQL binary log events.
You may implement your own handlers to handle events like INSERT, UPDATE and DELETE
with data of the affected rows.


## Requirements

*   MySQL >= 5.5
*   Python2 >= 2.7
*   [python-mysql-replication](https://github.com/noplay/python-mysql-replication):
    Pure Python Implementation of MySQL replication protocol build on top of PyMYSQL.
*   see `mysqlevp/handler/requirements.txt` for requirements of built-in handlers


## Installation

This package is currently in alpha version and not registered in PyPI. You can only install it with github.
```
pip install "git+https://github.com/jffifa/python-mysql-eventprocessor.git@master"
```


## MySQL Master Server Settings

MySQL Event Processor daemon behaves like a MySQL replication slave server,
so you need to [configure MySQL Master Server](https://dev.mysql.com/doc/refman/en/replication-howto-masterbaseconfig.html)
properly for binary log settings.

Here is an sample configuration for `my.cnf`
```
[mysqld]
server-id        = 1
log_bin          = /var/log/mysql/mysql-bin.log
expire_logs_days = 10
max_binlog_size  = 100M
# the binlog-format settings strongly affects implementations of
# the replication server
# be sure to set to "row" to receive INSERT, UPDATE and DELETE events.
# http://dev.mysql.com/doc/refman/en/binary-log.html
# http://dev.mysql.com/doc/refman/en/replication-formats.html
binlog-format    = row
```


## MySQL Replication User

The daemon will connect to MySQL master server as a replication slave,
so you must [create slave user](https://dev.mysql.com/doc/refman/en/replication-howto-repuser.html)
to connect master server.

Otherwise, you may use "root" user, which is not recommended in production environment.


## Usage

### Run as a Normal Program

1.  Choose an event handler or implement your own handler.
    See [Handler Developing](#handler-developing)
    for instructions in developing your own handlers.

2.  Write mysql connection settings.
    ```
    mysql_conn_settings = {
        'host':'127.0.0.1',
        'port':3306,
        'user':'root',
        'passwd':'password',
    }
    ```
    Be sure the account have appropriate privilege.

3.  Assign a unique [replication server ID](http://dev.mysql.com/doc/refman/en/replication-howto-slavebaseconfig.html) to the daemon.
    Do not conflict with other slave connected to the master server.

4.  Choose a path the daemon dump its status info to.
    Be sure that the daemon has write and read access to the directory of the path.

5.  Import `mysqlevp.deamon.MysqlevpWrapper` and create an instance with the params below.
    And then just run.
    ```
    from mysqlevp.daemon import MysqlevpWrapper
    mysqlevp = MysqlevpWrapper(
        mysql_conn_settings,
        replication_server_id=196883,
        my_event_handler,
        '/tmp/mysqlevp.dmp')
    mysqlevp.run()
    ```

See [`examples/write_to_console.py`](https://github.com/jffifa/python-mysql-eventprocessor/blob/master/examples/write_to_console.py)
for details and other options.

### Run as a Daemon Process

Use process manager like [supervisor](http://supervisord.org/) to control it,
or write your own python [DaemonContext](https://www.python.org/dev/peps/pep-3143/).


## Handler Developing

You should write a class derived from `mysqlevp.handler.base.IEventHandler`,
and implement the following 3 functions:

```
from mysqlevp.handler.base import IEventHandler

class MyHandler(IEventHandler):
    def on_insert(self, ev_id, ev_timestamp, schema, table, affected_rows):
        ...

    def on_update(self, ev_id, ev_timestamp, schema, table, affected_rows):
        ...

    def on_delete(self, ev_id, ev_timestamp, schema, table, affected_rows):
        ...
```

Read [`mysqlevp/handler/base.py`](https://github.com/jffifa/python-mysql-eventprocessor/blob/master/mysqlevp/handler/base.py)
for param documents and
the built-in handler [`mysqlevp/handler/console.py`](https://github.com/jffifa/python-mysql-eventprocessor/blob/master/mysqlevp/handler/console.py)
for example.

## TODO

*   Python3 support: Though using package `six` for compatibility, this project has not been tested under Python3 yet.
*   better logging utils
*   MySQL [Global Transaction Identifier](https://dev.mysql.com/doc/refman//en/replication-gtids-concepts.html) support.
*   Allow wild chars in table filters for database or table partions. (`CREATE TABLE t2 LIKE t` etc.)

## Similar Works

*   [meepo](https://github.com/eleme/meepo): Meepo is event sourcing and event broadcasting for databases.