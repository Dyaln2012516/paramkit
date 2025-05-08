# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : __init__.py.py
@Project  :
@Time     : 2025/4/6 21:10
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import getpass
import os
from datetime import datetime

from peewee import SQL, AutoField, CharField, DateTimeField, Model
from playhouse.pool import PooledSqliteDatabase

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'api.db')  # 修正为绝对路径

# 确保父目录存在
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

db = PooledSqliteDatabase(
    DATABASE_PATH,
    max_connections=32,  # Maximum connections
    stale_timeout=60,  # Idle connection timeout (seconds)
    check_same_thread=False,
    pragmas={
        'journal_mode': 'wal',
        'cache_size': -1024 * 10,  # 10MB cache
        'foreign_keys': 1,
    },
)


class BaseModel(Model):  # type: ignore
    id = AutoField(primary_key=True)
    # 新增字段
    updated_at = DateTimeField(
        default=datetime.now, constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')], formats='%Y-%m-%d %H:%M:%S'  # SQLite 需要这个约束
    )
    updated_by = CharField(
        max_length=32,
        default=getpass.getuser,
        help_text="operator",
    )

    def save(self, *args, **kwargs):
        # 在保存前自动更新 updated_at
        if self.id:  # 如果是更新操作
            self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = db


def init_db(*tables):
    # Safely create tables (only if they do not exist)
    db.create_tables(tables, safe=True)

    with db.connection():
        db.execute_sql('PRAGMA optimize;')
        db.execute_sql('ANALYZE;')
