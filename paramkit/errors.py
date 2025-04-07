# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : errors.py
@Project  : 
@Time     : 2025/3/28 17:38
@Author   : dylan
@Contact Email: cgq2012516@gmail.com
"""


class ParamError(Exception):
    """base error of the param"""


class ParamRepeatDefinedError(ParamError):
    """param repeated"""


class ParamMissingError(ParamError):
    """param missing"""


class ParamTypeError(ParamError):
    """param type error"""


class ParamLengthExceedLimitError(ParamError):
    """param length exceed limit"""


class ParamValueInvalidError(ParamError):
    """param invalid"""
