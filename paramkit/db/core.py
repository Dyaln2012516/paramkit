# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : core.py
@Project  : 
@Time     : 2025/4/8 16:39
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import json
import threading
from typing import Any, Callable, Dict, List, Union

from django.http import HttpRequest, JsonResponse
from peewee import DatabaseError, DoesNotExist
from rest_framework.request import Request

from paramkit.api.fields import P
from paramkit.db import db
from paramkit.db.model import APIHeaderRecord, APIParamRecord, APIRecord


class CollectDocs(threading.Thread):
    """collection of API documentation"""

    def __init__(
        self,
        *,
        request: Union[Request, HttpRequest],
        response: JsonResponse,
        view_func: Callable[..., Any],
        params: Dict[str, P],
        duration: float,
    ):
        super().__init__(daemon=False)
        self.params: Dict[str, P] = params
        self.request: Union[Request, HttpRequest] = request
        self.response: JsonResponse = response
        self.view_func: Callable[..., Any] = view_func
        self.duration: float = duration

    def run(self):
        self._start()

    @db.atomic()
    def _start(self):
        request_uid = self.upsert_record()
        self.upsert_headers(request_uid)
        self.upsert_params(request_uid)

    def upsert_record(self) -> str:

        new_record = APIRecord(
            method=self.request.method,
            path=self.request.path,
            status_code=self.response.status_code,
            client_ip=self.request.META.get("REMOTE_ADDR"),
            request_headers=json.dumps(dict(self.request.headers), indent=2),
            request_body=json.dumps(self.request.body.decode("utf-8", errors="replace"), indent=2),
            duration=self.duration,
            api_desc=self.view_func.__doc__,
        )
        try:
            record = (
                APIRecord.select().where((APIRecord.method == new_record.method) & (APIRecord.path == new_record.path)).get()
            )
            new_record.id = record.id
            new_record.request_uid = record.request_uid
        except DoesNotExist:
            pass
        finally:
            try:
                new_record.save()
            except DatabaseError:
                # 其他进程可能已插入，重新获取
                new_record = APIRecord.get(APIRecord.method == new_record.method, APIRecord.path == new_record.path)

        return new_record.request_uid

    def upsert_headers(self, request_uid: str):
        _ = APIHeaderRecord.delete().where(APIHeaderRecord.request_uid == request_uid).execute()

        headers: List[APIHeaderRecord] = []
        for k, v in self.request.headers.items():
            header = APIHeaderRecord(
                request_uid=request_uid,
                header_key=k,
                header_value=v,
            )
            headers.append(header)
        APIHeaderRecord.bulk_create(headers)

    def upsert_params(self, request_uid: str):
        _ = APIParamRecord.delete().where(APIParamRecord.request_uid == request_uid).execute()

        params: List[APIParamRecord] = []
        for p in self.params.values():
            param = APIParamRecord(
                request_uid=request_uid,
                param_name=p.name,
                param_type=p.typ.__name__,
                param_value=p.value,
                is_required=p.required,
                param_desc=p.desc,
                param_demo=str(p.opts) if p.opts else None,
            )
            params.append(param)
        APIParamRecord.bulk_create(params)
