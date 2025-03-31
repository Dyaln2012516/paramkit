# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : core.py
@Project  :
@Time     : 2025/3/28 17:29
@Author   : dylan
@Contact Email: cgq2012516@gmail.com
"""
from functools import wraps
from typing import Callable

from paramkit.cli import CliCommand
from paramkit.errors import ParamRepeatDefinedError
from paramkit.utils import web_params, flatten_params
from src.paramkit.fields import P


class ApiAssert:
    """
    A decorator class for API parameter validation.
    """
    __slots__ = ('_defineparams', 'enable_docs', 'attach')

    def __init__(self, *params: P, enable_docs: bool = False, attach: bool = False):
        """
        Initialize the ApiAssert decorator.

        :param params: List of parameter definitions
        :param enable_docs: Flag to enable documentation
        :param attach: Flag to attach validated data to the request
        """
        self._defineparams = dict()
        self.__setup__(params)
        self.enable_docs = enable_docs
        self.attach = attach

    def __call__(self, view_func):
        """
        Decorate the view function to validate parameters.

        :param view_func: The view function to be decorated
        :return: The decorated view function
        """

        @wraps(view_func)
        def _decorate(view_self, request, *view_args, **view_kwargs):
            # Flatten and validate parameters
            flatten_params(web_params(request, view_kwargs), self._defineparams)
            dataa = self.__validate__()

            if self.attach:
                request.dataa = dataa
            if self.enable_docs:
                self.__generate_docs__(view_func)

            rep = view_func(view_self, request, *view_args, **view_kwargs)
            return rep

        return _decorate

    def __setup__(self, ps):
        """
        Setup the parameter definitions and check for duplicates.

        :param ps: List of parameter definitions
        :raises ParamRepeatDefinedError: If a parameter is defined more than once
        """
        for p in ps:
            param_name = p.name
            if param_name in self._defineparams:
                raise ParamRepeatDefinedError(param_name)
            self._defineparams[param_name] = p

    def __validate__(self):
        """
        Validate all defined parameters.

        :return: Empty string after validation
        """
        for p in self._defineparams.values():
            p.validate()
        return ''

    def __generate_docs__(self, view_func):
        """生成API文档（示例）"""
        docs = ["Validated Parameters:"]
        for name, rule in self._defineparams.items():
            constraints = []
            if 'ge' in rule.constraints:
                constraints.append(f"min={rule.constraints['ge']}")
            if 'le' in rule.constraints:
                constraints.append(f"max={rule.constraints['le']}")
            if 'opts' in rule.constraints:
                constraints.append(f"options={rule.constraints['opts']}")

            docs.append(f"- {name} ({rule.type.__name__}): {', '.join(constraints)}")

        view_func.__doc__ = '\n'.join(docs)

    def cli_command(self, func: Callable) -> Callable:
        """添加 CLI 命令支持"""
        cli_handler = CliCommand(self)
        return cli_handler(func)


apiassert = ApiAssert
