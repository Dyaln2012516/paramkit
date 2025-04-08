# _*_ coding:utf-8 _*_
"""
@File     : fields.py
@Project  :
@Time     : 2025/3/28 17:34
@Author   : dylan
@Contact Email: cgq2012516@gmail.com
"""
import re
from typing import Any, List, Optional, Set, Tuple, Union

from paramkit.errors import ParamLengthExceedLimitError, ParamMissingError, ParamTypeError, ParamValueInvalidError


class P:
    """Parameter object representing a single parameter with various constraints."""

    __slots__ = (
        "name",
        "required",
        "typ",
        "opts",
        "lt",
        "gt",
        "le",
        "ge",
        "desc",
        "value",
        "url",
    )

    def __init__(
        self,
        name: str,
        /,
        *,
        required: bool = True,
        typ: Any = None,
        opts: Optional[Union[re.Pattern[str], str, List[Any], Tuple[Any, ...], Set[Any]]] = None,
        lt: Optional[Union[int, float]] = None,
        gt: Optional[Union[int, float]] = None,
        le: Optional[Union[int, float]] = None,
        ge: Optional[Union[int, float]] = None,
        desc: Optional[str] = None,
        default: Any = None,
    ):
        """
        Initialize a parameter with the given constraints.

        :param name: Name of the parameter
        :param required: Whether the parameter is mandatory
        :param typ: Expected type of the parameter
        :param opts: Allowed options for the parameter value
        :param lt: Less than constraint
        :param gt: Greater than constraint
        :param le: Less than or equal to constraint
        :param ge: Greater than or equal to constraint
        :param desc: Description of the parameter
        """
        self.name = name
        self.required = required
        self.typ = typ
        self.opts = opts
        self.lt = lt
        self.gt = gt
        self.le = le
        self.ge = ge
        self.desc = desc

        self.value = default
        self.url = None

        self.__check_bounds__()

    def __repr__(self):
        return f"P<{self.name}, type={self.typ.__name__}>"

    def __contains__(self, item):
        return item in self.__slots__

    def __check_bounds__(self) -> Optional[None]:
        """Check the parameter value range constraints."""
        lower = (
            max(
                ((self.ge, True), (self.gt, False)),
                key=lambda x: (x[0] if x[0] is not None else -float("inf"), not x[1]),
            )
            if any([self.ge, self.gt])
            else (None, None)
        )

        # Upper bound processing: take the strictest condition (smallest value and include equal priority)
        upper = (
            min(
                ((self.le, True), (self.lt, False)),
                key=lambda x: (x[0] if x[0] is not None else float("inf"), not x[1]),
            )
            if any([self.le, self.lt])
            else (None, None)
        )

        # Boundary validity check
        if lower[0] is not None and upper[0] is not None:
            # Numerical comparison
            if lower[0] > upper[0]:
                raise ValueError(f"Lower limit {lower[0]} exceeds upper limit {upper[0]}")

            # Check for closed interval at equal boundary values
            if lower[0] == upper[0] and not (lower[1] and upper[1]):
                raise ValueError(f"Boundary value {lower[0]} interval is not closed")

    def __validate_type__(self) -> Optional[None]:
        """Validate the type of the parameter value."""
        # Skip validation when type is None
        if self.typ is None:
            return

        if not isinstance(self.value, self.typ):
            if self.typ in (float, int) and str(self.value).replace(".", "", 1).isdigit():
                self.value = self.typ(self.value)
                return
            raise ParamTypeError(f"Expected type {self.typ.__name__} but got {type(self.value).__name__}")

    def __validate_value__(self) -> Optional[None]:
        """Validate the parameter value against the allowed options."""
        if self.value is None:
            raise ParamMissingError(f"param `{self.name}` is required")

        if self.opts is None:
            return

        if not (
            (isinstance(self.opts, re.Pattern) and self.opts.fullmatch(str(self.value)))
            or (isinstance(self.opts, str) and re.fullmatch(self.opts, str(self.value)))
            or (isinstance(self.opts, (list, tuple)) and self.value in self.opts)
        ):
            raise ParamValueInvalidError(f"param `{self.name}` value is invalid, current: {self.value}, expected: {self.opts}")

    def __validate_limit__(self) -> Optional[None]:
        """Validate the parameter value against range constraints."""
        value = len(self.value) if isinstance(self.value, (str, list, tuple, dict, set)) else self.value
        if not (
            (self.ge is None or value >= self.ge)
            and (self.gt is None or value > self.gt)
            and (self.le is None or value <= self.le)
            and (self.lt is None or value < self.lt)
        ):
            raise ParamLengthExceedLimitError(f"param `{self.name}` is out of limitation, current: {value}")

    def validate(self) -> Optional[None]:
        """Validate the parameter value against all constraints."""
        # Skip validation when not required and value is None
        if not self.required and self.value is None:
            return

        self.__validate_value__()
        self.__validate_type__()
        self.__validate_limit__()
