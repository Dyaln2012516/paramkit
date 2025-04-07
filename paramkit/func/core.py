# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : core.py
@Project  : 
@Time     : 2025/4/2 09:21
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import abc
import inspect
import sys
from functools import lru_cache, wraps
from typing import Any, Callable, ForwardRef, List, Optional, Type, Union, get_args, get_origin

from paramkit.errors import ParamTypeError
from paramkit.typing import AssertParamT


class CheckerContext:
    """类型解析上下文"""

    __slots__ = ('globals_', 'locals_', 'type_params')

    def __init__(self, globals_: dict[str, Any], locals_: dict[str, Any] = None, type_params: dict[str, Any] = None):
        self.globals_ = globals_
        self.locals_ = locals_ or {}
        self.type_params = type_params or {}


class BaseChecker(metaclass=abc.ABCMeta):
    """检查器基类"""

    __slots__ = ('ctx', 'hint')

    def __init__(self, ctx: CheckerContext, hint: Any):
        self.ctx = ctx
        self.hint = hint

    @classmethod
    @abc.abstractmethod
    def supports(cls, hint: Any) -> bool:
        """是否支持该类型注解"""
        raise NotImplementedError

    @abc.abstractmethod
    def check(self, value: Any) -> bool:
        """执行类型检查"""
        raise NotImplementedError

    @classmethod
    def create(cls, ctx: CheckerContext, hint: Any) -> 'BaseChecker':
        """创建检查器实例"""
        return cls(ctx, hint)


# ----------------------
# 内置检查器实现
# ----------------------
class SimpleTypeChecker(BaseChecker):
    """基础类型检查器（int/str等）"""

    @classmethod
    def supports(cls, hint: Any) -> bool:
        return isinstance(hint, type) or hint is Any

    def check(self, value: Any) -> bool:
        if self.hint is Any:
            return True
        return isinstance(value, self.hint)


class UnionChecker(BaseChecker):
    """联合类型检查器"""

    @classmethod
    def supports(cls, hint: Any) -> bool:
        return get_origin(hint) is Union

    def __init__(self, ctx: CheckerContext, hint: Any):
        super().__init__(ctx, hint)
        self.checkers: List[Callable[[Any], bool]] = [checker_factory(ctx, arg).check for arg in get_args(hint)]

    def check(self, value: Any) -> bool:
        return any(check(value) for check in self.checkers)


class ListChecker(BaseChecker):
    """列表类型检查器"""

    @classmethod
    def supports(cls, hint: Any) -> bool:
        origin = get_origin(hint)
        return origin in (list, List)

    def __init__(self, ctx: CheckerContext, hint: Any):
        super().__init__(ctx, hint)
        elem_hint = get_args(hint)[0]
        self.elem_checker = checker_factory(ctx, elem_hint)

    def check(self, value: Any) -> bool:
        return isinstance(value, list) and all(self.elem_checker.check(elem) for elem in value)


class ForwardRefChecker(BaseChecker):
    """前向引用检查器"""

    @classmethod
    def supports(cls, hint: Any) -> bool:
        return isinstance(hint, (str, ForwardRef))

    def __init__(self, ctx: CheckerContext, hint: Any):
        super().__init__(ctx, hint)
        resolved = self._resolve_forward_ref(hint)
        self.checker = checker_factory(ctx, resolved)

    def _resolve_forward_ref(self, hint: Any) -> Any:
        ref = ForwardRef(hint) if isinstance(hint, str) else hint
        if ref.__forward_value__ is not None:
            return ref.__forward_value__(self.ctx.globals_, self.ctx.locals_)
        return ref

    def check(self, value: Any) -> bool:
        return self.checker.check(value)


# ----------------------
# 检查器注册与工厂
# ----------------------
_CHECKER_REGISTRY: List[Type[BaseChecker]] = [
    SimpleTypeChecker,
    UnionChecker,
    ListChecker,
    ForwardRefChecker,
]


def register_checker(checker_cls: Type[BaseChecker], priority: int = 0):
    """注册自定义检查器"""
    _CHECKER_REGISTRY.insert(priority, checker_cls)


@lru_cache(maxsize=1024)
def checker_factory(ctx: CheckerContext, hint: Any) -> BaseChecker:
    """创建类型检查器（带缓存）"""
    for checker_cls in _CHECKER_REGISTRY:
        if checker_cls.supports(hint):
            return checker_cls.create(ctx, hint)
    raise TypeError(f"Unsupported type hint: {hint}")


# ----------------------
# 装饰器实现
# ----------------------


def unwrap_func(obj: Any) -> Any:
    """
    递归解开所有装饰器，返回原始对象（函数、property 或类）
    - 支持 @classmethod/@staticmethod/@property
    - 自动处理任意层数的普通装饰器（需正确使用 @functools.wraps）
    """
    # 处理 property 对象
    if isinstance(obj, property):
        if obj.fget is not None:
            return unwrap_func(obj.fget)
        return obj  # 无法解包没有 fget 的 property

    # 处理 classmethod/staticmethod
    if isinstance(obj, (classmethod, staticmethod)):
        return unwrap_func(obj.__func__)

    # 处理实例方法（如 obj.method）
    if inspect.ismethod(obj):
        return unwrap_func(obj.__func__)

    # 处理普通装饰器（递归解开 __wrapped__）
    raw_func = obj
    while hasattr(raw_func, '__wrapped__'):
        raw_func = raw_func.__wrapped__
        # 继续解包可能存在的嵌套装饰器
        raw_func = unwrap_func(raw_func)

    return raw_func


def funcassert(decorated_obj: Optional[AssertParamT] = None, *, assert_return=False):
    """类型检查装饰器"""

    def decorator(func, instance=None):
        ctx = CheckerContext(globals_=sys.modules[func.__module__].__dict__)
        sig = inspect.signature(func)

        # 预编译参数检查器
        param_checkers = {
            param_name: checker_factory(ctx, param.annotation)
            for param_name, param in sig.parameters.items()
            if param.annotation is not inspect.Parameter.empty
        }

        # 预编译返回值检查器
        return_hint = sig.return_annotation
        return_checker = checker_factory(ctx, return_hint) if return_hint is not inspect.Parameter.empty else None

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 参数检查
            try:
                bound = sig.bind(*args, **kwargs)
            # 可能是类方法或者实例方法
            except TypeError as ex:
                if not instance:
                    raise ex
                bound = sig.bind(*args[1:], **kwargs)

            for param_name, value in bound.arguments.items():
                if checker := param_checkers.get(param_name):
                    if not checker.check(value):
                        raise ParamTypeError(
                            f"`{func.__qualname__}`参数`{param_name}`类型错误, 目标类型:{checker.hint}, 实际类型{type(value)}"
                        )  # noqa：C0301

            # 执行函数
            result = func(*args, **kwargs)

            # 返回值检查
            if assert_return and return_checker:
                if not return_checker.check(result):
                    raise ParamTypeError(
                        f"`{func.__qualname__}`返回值类型错误,expected: {return_hint}, current: {type(result)}"
                    )

            return result

        return wrapper

    def decorator_cls(cls: Type) -> Type:
        for name, method in inspect.getmembers(cls, lambda i: inspect.ismethod(i) or inspect.isfunction(i)):
            setattr(cls, name, decorator(method, instance=cls))
        return cls

    # 处理类装饰
    if inspect.isclass(decorated_obj):
        return decorator_cls(decorated_obj)

    return decorator(decorated_obj) if decorated_obj else lambda o: decorator_cls(o) if inspect.isclass(o) else decorator
