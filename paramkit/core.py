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


apiassert = ApiAssert


class Request:
    """
    Mock request class for testing purposes.
    """

    def __init__(self):
        self.name = "cgq"
        self.age = 18
        self.addr = {
            'road': 'Traffic Street',
            'district': 'Caiyuanba',
            'home': 'qt',
            'school': {
                'teacher': 'ydy',
                'class': 1,
                'subject': 'math',
                'score': 100
            }
        }
        self.hobbies = [
            'shooting',
            'fishing',
            'swimming',
            'running',
            'dancing',
            'sleeping',
            'eating',
            'coding',
            'playing',
            'watching',
            'reading',
            'writing',
            'singing',
        ]
        self.method = 'GET'

    @property
    def GET(self):
        return self

    def dict(self):
        return self.__dict__


class DemoView:
    """
    Demo view class to demonstrate parameter validation.
    """

    @apiassert(
        P('name', typ=str, gt=2, le=3, opts=('cgq', 'b'), must=False),
        P('age', typ=int, ge=2, le=100),
        P('addr', typ=dict, le=10, ge=2),
        P('hobbies', typ=list, ge=1, le=16),
        P('addr.school.teacher', typ=str, ge=2, le=6, opts=('xz', 'ydy')),
    )
    def view_func(self, request):
        """
        Example view function to demonstrate parameter validation.

        :param request: The request object
        """
        print(request)


if __name__ == "__main__":
    # demo = DemoView()
    # demo.view_func(Request())
    print('4.3'.isdecimal())
