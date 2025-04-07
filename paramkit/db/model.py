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
    """Supported HTTP methods enumeration"""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class APIRecord(BaseModel):
    """
    API request record model

    Attributes:
        timestamp: Request time, automatically records creation time
        method: HTTP method, only allows predefined types
        path: Request path, creates a normal index
        status_code: Response status code, can be null (may be no response if request fails)
        client_ip: Client IP address, supports up to IPv6 format
        request_headers: Request headers, stored as JSON string
        request_body: Raw request body content
        response_headers: Response headers, stored as JSON string
        response_body: Raw response body content
        duration: Request processing time (seconds), floating-point precision
    """

    # Timestamp (automatically recorded)
    timestamp = DateTimeField(
        default=datetime.now, index=True, help_text="Time of the request, automatically recorded as the record creation time"
    )

    # HTTP method (enum validation)
    method = CharField(
        max_length=10,
        index=True,
        choices=[(m.value, m.name) for m in HTTPMethod],  # Enum value validation
        constraints=[Check(f"method IN {tuple(m.value for m in HTTPMethod)}")],  # Database level validation
        help_text="HTTP request method, only allows the following values: " + ', '.join(m.value for m in HTTPMethod),
    )

    # Request path (creates an index)
    path = TextField(index=True, help_text="Full request path, maximum length 2000 characters")

    # Response status code (can be null)
    status_code = IntegerField(
        null=True,
        constraints=[Check('status_code BETWEEN 100 AND 599')],  # Status code range validation
        help_text="HTTP status code, range 100-599, may be null if request fails",
    )

    # Client information
    client_ip = CharField(max_length=45, help_text="Client IP address, supports IPv6 format")

    # Request data
    request_headers = TextField(help_text="Request headers in JSON format, example: {'Content-Type':'application/json'}")
    request_body = TextField(null=True, help_text="Raw request body content, maximum length 10MB")

    # Response data
    response_headers = TextField(help_text="Response headers in JSON format")
    response_body = TextField(null=True, help_text="Raw response body content, maximum length 10MB")

    # Performance metrics
    duration = FloatField(
        help_text="Request processing time (seconds), precision to milliseconds", constraints=[Check('duration >= 0')]
    )  # Non-negative validation

    class Meta:
        table_name = 'api_record'
        indexes = (
            # Composite index example: commonly used for status code analysis
            (('method', 'status_code'), False),
            # Covering index: optimizes time range queries
            (('timestamp', 'duration'), False),
            (('path', 'method'), True),
        )
        constraints = [
            # Multi-column CHECK supported in database version >=3.25
            Check('LENGTH(path) <= 2000')
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code or 'No Response'}"


init_db([APIRecord])
