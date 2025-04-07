# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : model.py
@Project  : 
@Time     : 2025/4/6 21:40
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""

from datetime import datetime
from enum import Enum

from peewee import CharField, DateTimeField, FloatField, IntegerField, TextField
from playhouse.sqlite_ext import Check

from paramkit.db import BaseModel, init_db


class HTTPMethod(str, Enum):
    """支持的HTTP方法枚举"""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class APIRecord(BaseModel):
    """
    API请求记录模型

    Attributes:
        timestamp: 请求时间，自动记录创建时间
        method: HTTP方法，仅允许预定义类型
        path: 请求路径，建立普通索引
        status_code: 响应状态码，允许为空（请求失败时可能无响应）
        client_ip: 客户端IP地址，最长支持IPv6格式
        request_headers: 请求头，存储为JSON字符串
        request_body: 原始请求体内容
        response_headers: 响应头，存储为JSON字符串
        response_body: 原始响应体内容
        duration: 请求处理耗时（秒），浮点数精度
    """

    # 时间戳（自动记录）
    timestamp = DateTimeField(default=datetime.now, index=True, help_text="请求发生的时间，自动记录为记录创建时间")

    # HTTP方法（枚举验证）
    method = CharField(
        max_length=10,
        index=True,
        choices=[(m.value, m.name) for m in HTTPMethod],  # 枚举值验证
        constraints=[Check(f"method IN {tuple(m.value for m in HTTPMethod)}")],  # 数据库层校验
        help_text="HTTP请求方法，仅允许以下值：" + ', '.join(m.value for m in HTTPMethod),
    )

    # 请求路径（建立索引）
    path = TextField(index=True, help_text="请求的完整路径，最大长度2000字符")

    # 响应状态码（允许为空）
    status_code = IntegerField(
        null=True,
        constraints=[Check('status_code BETWEEN 100 AND 599')],  # 状态码范围校验
        help_text="HTTP状态码，范围100-599，请求失败时可能为空",
    )

    # 客户端信息
    client_ip = CharField(max_length=45, help_text="客户端IP地址，支持IPv6格式")

    # 请求数据
    request_headers = TextField(help_text="JSON格式的请求头，示例：{'Content-Type':'application/json'}")
    request_body = TextField(null=True, help_text="原始请求体内容，最大长度10MB")

    # 响应数据
    response_headers = TextField(help_text="JSON格式的响应头")
    response_body = TextField(null=True, help_text="原始响应体内容，最大长度10MB")

    # 性能指标
    duration = FloatField(help_text="请求处理耗时（秒），精度到毫秒", constraints=[Check('duration >= 0')])  # 非负校验

    class Meta:
        table_name = 'api_records'
        indexes = (
            # 复合索引示例：常用于状态码分析
            (('method', 'status_code'), False),
            # 覆盖索引：优化时间段查询
            (('timestamp', 'duration'), False),
        )
        constraints = [
            # 数据库版本>=3.25时支持多列CHECK
            Check('LENGTH(path) <= 2000')
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code or 'No Response'}"


init_db([APIRecord])
