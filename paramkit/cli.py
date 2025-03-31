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
from typing import Any, Dict, Callable, Union

from paramkit.fields import P


class CliCommand:
    """CLI 命令生成扩展"""

    def __init__(self, api_assert: 'ApiAssert'):
        self.api_assert = api_assert
        self.parser = argparse.ArgumentParser()
        self._build_parser()

    def _convert_type(self, param_type) -> Callable:
        """类型转换处理器"""
        type_map = {
            list: lambda x: x.split(','),
            dict: lambda x: dict(pair.split(':') for pair in x.split(',')),
            bool: lambda x: x.lower() in ('true', '1', 'yes')
        }
        return type_map.get(param_type, param_type)

    def _build_argument(self, param: P):
        """构建单个命令行参数"""
        arg_name = f"--{param.name.replace('.', '-')}"
        help_parts = [f"Type: {param.type.__name__}"]

        # 约束条件描述
        if 'ge' in param.constraints:
            help_parts.append(f"min={param.constraints['ge']}")
        if 'le' in param.constraints:
            help_parts.append(f"max={param.constraints['le']}")
        if 'opts' in param.constraints:
            opts = ', '.join(param.constraints['opts'])
            help_parts.append(f"options: {opts}")

        # 参数配置
        arg_config = {
            'type': self._convert_type(param.type),
            'help': ' | '.join(help_parts),
            'required': param.must,
            'default': param.constraints.get('default', None)
        }

        self.parser.add_argument(arg_name, **arg_config)

    def _build_parser(self):
        """构建完整的参数解析器"""
        for param in self.api_assert._defineparams.values():
            self._build_argument(param)

    def __call__(self, func: Callable) -> Callable:
        """生成 CLI 执行逻辑"""

        @wraps(func)
        def wrapped(*args, **kwargs):
            cli_args = vars(self.parser.parse_args())
            validated = self.api_assert._ApiAssert__validate_params(cli_args)  # 复用验证逻辑
            return func(**validated)

        return wrapped
