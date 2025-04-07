# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : __init__.py.py
@Project  :
@Time     : 2025/4/6 21:10
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from peewee import Model
from playhouse.pool import PooledSqliteDatabase

db = PooledSqliteDatabase(
    'data/api.db',
    max_connections=20,  # Maximum connections
    stale_timeout=300,  # Idle connection timeout (seconds)
    check_same_thread=False,
    pragmas={
        'journal_mode': 'wal',
        'cache_size': -1024 * 10,  # 10MB cache
        'foreign_keys': 1,
    },
)


class BaseModel(Model):  # type: ignore
    class Meta:
        database = db


def init_db(*tables):
    # Safely create tables (only if they do not exist)
    db.create_tables(*tables, safe=True)

    with db.connection():
        db.execute_sql('PRAGMA optimize;')
        db.execute_sql('ANALYZE;')
