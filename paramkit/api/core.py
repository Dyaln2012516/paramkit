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
from functools import wraps
from typing import Callable, Dict, Optional, Tuple

from paramkit.api.fields import P
from paramkit.db.core import CollectDocs
from paramkit.errors import ParamRepeatDefinedError
from paramkit.utils import flatten_params, web_params


class ApiAssert:
    """
    A decorator class for API parameter validation.
    """

    __slots__ = ("defined_params", "enable_docs")

    def __init__(self, *params: P, enable_docs: bool = False):
        """
        Initialize the ApiAssert decorator.

        :param params: List of parameter definitions
        :param enable_docs: Flag to enable documentation
        :param attach: Flag to attach validated data to the request
        """
        self.defined_params: Dict[str, P] = {}
        self.__setup__(params)
        self.enable_docs = enable_docs

    def __call__(self, view_func):
        """
        Decorate the view function to validate parameters.

        :param view_func: The view function to be decorated
        :return: The decorated view function
        """

        @wraps(view_func)
        def _decorate(view_self, request, *view_args, **view_kwargs):
            # Flatten and validate parameters
            flatten_params(web_params(request, view_kwargs), self.defined_params)
            self.__validate__()
            start = time.perf_counter()
            rep = view_func(view_self, request, *view_args, **view_kwargs)
            duration = (time.perf_counter() - start) * 1000
            if self.enable_docs:
                CollectDocs(
                    request=request, response=rep, view_func=view_func, params=self.defined_params, duration=duration
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

    def __validate__(self) -> None:
        """
        Validate all defined parameters.

        :return: Empty string after validation
        """
        for p in self.defined_params.values():
            p.validate()

    def __generate_docs__(self, view_func: Callable[..., None]) -> Optional[None]:
        """Generate API documentation (example)"""
        docs = ["Validated Parameters:"]
        for name, param in self.defined_params.items():
            constraints = []
            if "ge" in param:
                constraints.append(f"min={param.ge}")
            if "le" in param:
                constraints.append(f"max={param.le}")
            if "opts" in param:
                constraints.append(f"options={param.opts}")

            docs.append(f"- {name} ({param.typ.__name__}): {', '.join(constraints)}")

        view_func.__doc__ = "\n".join(docs)

    # def cli_command(self, func: Callable[..., None]) -> Callable[..., Any]:
    #     """Add CLI command support"""
    #     cli_handler = CliCommand(self)
    #     return cli_handler(func)


apiassert = ApiAssert  # noqa: C0103
