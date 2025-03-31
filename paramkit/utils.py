# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : utils.py
@Project  :
@Time     : 2025/3/28 17:34
@Author   : dylan
@Contact Email: cgq2012516@gmail.com
"""
import json
from typing import Any, Dict
from django.http import HttpRequest

from rest_framework.request import Request
from paramkit.fields import P


def web_params(request: HttpRequest, view_kwargs: Dict[str, Any] = None) -> Dict:
    """
    Retrieve all request parameters in a unified manner.
    Supports: query parameters, form data, JSON body, URL path parameters, file uploads.
    Compatible with: Django View and DRF APIView.

    :param request: Request object (Django or DRF)
    :param view_kwargs: View's self.kwargs (path parameters)
    :return: Merged parameter dictionary
    """
    params = {}

    # Handle query parameters
    if isinstance(request, Request):
        # DRF's query_params is an enhanced version of the native QueryDict
        params.update(request.query_params.dict())
    else:
        # Native Django GET parameters
        params.update(request.GET.dict())

    # Handle request body parameters
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        content_type = request.content_type

        # DRF has already parsed the data into request.data
        if isinstance(request, Request):
            params.update(request.data)
        else:
            # Native Django handling logic
            if content_type == "application/json":
                try:
                    params.update(json.loads(request.body))
                except json.JSONDecodeError:
                    pass
            elif content_type in ["application/x-www-form-urlencoded", "multipart/form-data"]:
                params.update(request.POST.dict())
                # Handle file uploads
                params.update({name: request.FILES.getlist(name) for name in request.FILES})

    # Merge path parameters
    if view_kwargs:
        params.update(view_kwargs)

    return params


def flatten_params(webparams: Dict[str, Any], defineparams: Dict[str, P]) -> None:
    """
    Flatten nested parameters and set values in the defined parameters.

    :param webparams: Dictionary of web parameters
    :param defineparams: Dictionary of defined parameters
    """

    def _setvalue(name, value):
        if param := defineparams.get(name):
            param.value = value

    def _flatten(obj, prefix=''):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                _flatten(value, prefix=full_key)
            _setvalue(full_key, value)

    _flatten(webparams)
