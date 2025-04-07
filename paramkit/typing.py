# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : typing.py
@Project  : 
@Time     : 2025/4/2 13:15
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from typing import Any, Callable, TypeVar, Union

MethodDecoratorClassType = classmethod
MethodDecoratorPropertyType = property
MethodDecoratorStaticType = staticmethod
CallableAny = Callable[..., Any]

AssertParamT = TypeVar(
    'AssertParamT',
    bound=Union[
        type,
        CallableAny,
        MethodDecoratorClassType,
        MethodDecoratorPropertyType,
        MethodDecoratorStaticType,
        # MethodBoundInstanceOrClassType,
    ],
)
