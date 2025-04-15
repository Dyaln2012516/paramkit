# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : core.py
@Project  :
@Time     : 2025/3/28 17:29
@Author   : dylan
@Contact Email: cgq2012516@gmail.com
"""
import time
from copy import deepcopy
from functools import wraps
from typing import Dict, Tuple

from paramkit.api.fields import P
from paramkit.db.core import CollectDocs
from paramkit.errors import ParamRepeatDefinedError
from paramkit.utils import flatten_params, web_params

try:
    from django.conf import settings

    DEBUG = settings.DEBUG

except ImportError:
    DEBUG = False


class ApiAssert:
    """
    A decorator class for API parameter validation.
    """

    __slots__ = ("defined_params", "enable_docs", "api_desc")

    def __init__(
        self,
        *params: P,
        enable_docs: bool = False,
        api_desc: str = '',
    ):
        """
        Initialize the ApiAssert decorator.

        :param params: List of parameter definitions
        :param enable_docs: Flag to enable documentation
        :param api_desc: description of the API
        """
        self.defined_params: Dict[str, P] = {}
        self.__setup__(params)
        self.enable_docs = enable_docs
        self.api_desc = api_desc

    def __call__(self, view_func):
        """
        Decorate the view function to validate parameters.

        :param view_func: The view function to be decorated
        :return: The decorated view function
        """

        @wraps(view_func)
        def _decorate(view_self, request, *view_args, **view_kwargs):
            # Flatten and validate parameters
            request_params = web_params(request, view_kwargs)
            params_bak = deepcopy(self.defined_params)
            flatten_params(request_params, params_bak)
            self.__validate__(params_bak)
            start = time.perf_counter()
            try:
                rep = view_func(view_self, request, *view_args, **view_kwargs)
            except Exception as e:  # pylint: disable=bare-except
                # Handle exceptions and log them if needed
                raise e

            duration = (time.perf_counter() - start) * 1000
            if self.enable_docs or DEBUG:
                CollectDocs(
                    request_params,
                    request=request,
                    response=rep,
                    view_func=view_func,
                    params=self.defined_params,
                    duration=duration,
                    api_desc=self.api_desc,
                ).start()

            return rep

        return _decorate

    def __setup__(self, ps: Tuple[P, ...]):
        """
        Setup the parameter definitions and check for duplicates.

        :param ps: List of parameter definitions
        :raises ParamRepeatDefinedError: If a parameter is defined more than once
        """
        for p in ps:
            param_name = p.name
            if param_name in self.defined_params:
                raise ParamRepeatDefinedError(param_name)
            self.defined_params[param_name] = p

    @staticmethod
    def __validate__(params: dict[str, P]) -> None:
        """
        Validate all defined parameters.

        :return: Empty string after validation
        """
        for p in params.values():
            p.validate()


apiassert = ApiAssert  # noqa: C0103
