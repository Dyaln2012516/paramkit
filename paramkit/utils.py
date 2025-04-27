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
from typing import Any, Dict, Optional, Union

from django.http import HttpRequest
from rest_framework.request import Request

from paramkit.api.fields import P


def content_type_in(ct: str, *cts: str) -> bool:
    return any(ct.startswith(c) for c in cts)


def web_params(request: HttpRequest, view_kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retrieve all request parameters in a unified manner.
    Supports: query parameters, form data, JSON body, URL path parameters, file uploads.
    Compatible with: Django View and DRF APIView.

    :param request: Request object (Django or DRF)
    :param view_kwargs: View's self.kwargs (path parameters)
    :return: Merged parameter dictionary
    """
    params = {}
    # Merge path parameters
    if view_kwargs:
        params.update(view_kwargs)

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
        # Native Django handling logic
        if content_type_in(content_type, "application/json"):
            # DRF has already parsed the data into request.data
            if isinstance(request, Request):
                params.update(request.data)
            else:
                try:
                    params.update(json.loads(request.body))
                except json.JSONDecodeError:
                    pass
        elif content_type_in(
            content_type,
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ):
            params.update({key: values if len(values) > 1 else values[0] for key, values in request.POST.lists()})
            # Handle file uploads
            # params.update({name: request.FILES.getlist(name) for name in request.FILES})

    return params


def flatten_params(webparams: Dict[str, Any], defined_params: Dict[str, P]) -> None:
    """
    Flatten nested parameters and set values in the defined parameters.

    :param webparams: Dictionary of web parameters
    :param defined_params: Dictionary of defined parameters
    """

    def _setvalue(name: str, value: Union[int, float, dict[str, Any], list[Any], str, bool]):
        if param := defined_params.get(name):
            param.value = value

    def _flatten(obj: Any, prefix: str = ""):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                _flatten(value, prefix=full_key)
            _setvalue(full_key, value)

    _flatten(webparams)
