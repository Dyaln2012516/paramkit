# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : cli.py
@Project  :
@Time     : 2025/3/31 14:26
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import argparse
from functools import wraps
from typing import Any, Callable, Optional

from paramkit.api.fields import P


class CliCommand:
    """CLI command generation extension"""

    def __init__(self, api_assert):
        self.api_assert = api_assert
        self.parser = argparse.ArgumentParser()
        self._build_parser()

    @staticmethod
    def convert_type(param_type) -> Callable[[str], Any]:
        """Type conversion handler"""
        type_map = {
            list: lambda x: x.split(","),
            dict: lambda x: dict(pair.split(":") for pair in x.split(",")),
            bool: lambda x: x.lower() in ("true", "1", "yes"),
        }
        return type_map.get(param_type, param_type)

    def _build_argument(self, param: P):
        """Build a single command line argument"""
        arg_name = f"--{param.name.replace('.', '-')}"
        help_parts = [f"Type: {param.typ.__name__}"]

        # Constraint description
        if "ge" in param:
            help_parts.append(f"min={param.ge}")
        if "le" in param:
            help_parts.append(f"max={param.le}")
        # if "opts" in param:
        #     opts = ", ".join(param.opts)
        #     help_parts.append(f"options: {opts}")

        # Argument configuration
        arg_config = {
            "type": self.convert_type(param.typ),
            "help": " | ".join(help_parts),
            "required": param.required,
            "default": param.value,
        }

        self.parser.add_argument(arg_name, **arg_config)

    def _build_parser(self) -> Optional[None]:
        """Build the complete argument parser"""
        for param in self.api_assert.defined_params.values():
            self._build_argument(param)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Generate CLI execution logic"""

        @wraps(func)
        def wrapped(*args, **kwargs):  # noqa: W0613
            cli_args = vars(self.parser.parse_args())
            validated = self.api_assert(cli_args)  # Reuse validation logic
            return func(**validated)

        return wrapped
