# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : __init__.py.py
@Project  : 
@Time     : 2025/4/6 21:10
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from typing import Type, TypeVar

from peewee import Model
from playhouse.pool import PooledSqliteDatabase

db = PooledSqliteDatabase(
    'data/api.db',
    max_connections=20,  # 最大连接数
    stale_timeout=300,  # 闲置连接超时（秒）
    check_same_thread=False,
    pragmas={
        'journal_mode': 'wal',
        'cache_size': -10240,  # 10MB缓存
        'foreign_keys': 1,
    },
)


class BaseModel(Model):  # type: ignore
    class Meta:
        database = db


def init_db(*tables):
    # 安全创建表（仅当表不存在时）
    db.create_tables(*tables, safe=True)

    # 初始化后立即执行优化
    with db:
        db.execute('PRAGMA optimize;')
        db.execute('ANALYZE;')
