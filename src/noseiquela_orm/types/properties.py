from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from dateutil.parser import parse
from proto.datetime_helpers import DatetimeWithNanoseconds

from .base import BaseProperty

if TYPE_CHECKING:
    from typing import Any, Callable, Optional
    from typing import (
        Optional, Union, Any, Callable, Tuple, Set, Dict, List
    )


class BooleanProperty(BaseProperty):
    def __init__(
        self,
        *,
        required: 'bool'=False,
        default: 'Optional[Union[bool, int]]'=None,
        choices: 'Optional[Union[List[bool], Tuple[bool], Dict[Any, bool], Set[bool]]]'=None,
        validation: 'Optional[Callable[[bool], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        super().__init__(
            required=required,
            default=default,
            choices=choices,
            validation=validation,
            _prop_name=_prop_name,
        )

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        value = True if value in [True, 1] else value
        value = False if value in [False, 0] else value

        if self._choices and value not in self._choices:
            raise ValueError(f"'{value}' is not in choices ({self.choices})")

        if self._choices and isinstance(self._choices, dict) and value in self._choices:
            value = self.choices[value]

        if not isinstance(value, bool):
            raise ValueError(f"'{self._property_name}' must be a 'bool'")

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        return value


class DateTimeProperty(BaseProperty):
    def __init__(
        self,
        *,
        required: 'bool'=False,
        force_string: 'bool'=False,
        default: 'Optional[Union[datetime, Callable[[], datetime]]]'=None,
        choices: 'Optional[Union[List, Tuple, Dict, Set]]'=None,
        validation: 'Optional[Callable[[bool], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        super().__init__(
            required=required,
            default=default,
            choices=choices,
            validation=validation,
            _prop_name=_prop_name,
        )
        self._force_string = force_string

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        if not isinstance(value, (datetime, str, DatetimeWithNanoseconds)):
            raise Exception((
                f"'{self._property_name}' must be a "
                "'str', 'datetime' or 'DatetimeWithNanoseconds' instance."
            ))

        if isinstance(value, DatetimeWithNanoseconds):
            value = value.isoformat()

        if isinstance(value, str):
            value = parse(value)

        if self._choices and value not in self._choices:
            raise ValueError(f"'{value}' is not in choices ({self.choices})")

        if self._choices and isinstance(self._choices, dict) and value in self._choices:
            value = self.choices[value]

        if not isinstance(value, datetime):
            raise ValueError(f"'{self._property_name}' must be a 'bool'")

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        if self._force_string:
            return value.isoformat()

        return value


class FloatProperty(BaseProperty):
    def __init__(
        self,
        *,
        min: 'Optional[Union[float, str]]'=None,
        max: 'Optional[Union[float, str]]'=None,
        force_string: 'bool'=False,
        required: 'bool'=False,
        default: 'Optional[Union[bool, int]]'=None,
        validation: 'Optional[Callable[[bool], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        if min is not None and not isinstance(min, (int, str, float)):
            raise Exception()

        if max is not None and not isinstance(max, (int, str, float)):
            raise Exception()

        super().__init__(
            required=required,
            default=default,
            validation=validation,
            _prop_name=_prop_name,
        )
        self._force_string = force_string
        self._min_value = None if min is None else str(min)
        self._max_value = None if max is None else str(max)

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        if not isinstance(value, (int, float, str)):
            raise Exception((
                f"'{self._property_name}' must be a "
                "'float' or 'str' instance."
            ))

        value = Decimal(str(value))

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        if ((self._min_value is not None and value < Decimal(self._min_value)) or
            (self._max_value is not None and value > Decimal(self._max_value))):
            raise Exception((
                f"'{self._property_name}' out of defined range: {value}. "
                f"max: {self._max_value} | min: {self._min_value}"
            ))

        if self._force_string:
            return str(value)

        return float(value)


class IntegerProperty(BaseProperty):
    def __init__(
        self,
        *,
        min: 'Optional[Union[float, str]]'=None,
        max: 'Optional[Union[float, str]]'=None,
        required: 'bool'=False,
        default: 'Optional[Union[bool, int]]'=None,
        choices: 'Optional[Union[List, Tuple, Dict, Set]]'=None,
        validation: 'Optional[Callable[[bool], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        if min is not None and not isinstance(min, int):
            raise Exception()

        if max is not None and not isinstance(max, int):
            raise Exception()

        super().__init__(
            required=required,
            default=default,
            choices=choices,
            validation=validation,
            _prop_name=_prop_name,
        )
        self._min_value = min
        self._max_value = max

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        if self._choices and value not in self._choices:
            raise ValueError(f"'{value}' is not in choices ({self.choices})")

        if self._choices and isinstance(self._choices, dict) and value in self._choices:
            value = self.choices[value]

        if not isinstance(value, int):
            raise ValueError(f"'{self._property_name}' must be a 'bool'")

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        if ((self._min_value is not None and value < self._min_value) or
            (self._max_value is not None and value > self._max_value)):
            raise Exception((
                f"'{self._property_name}' out of defined range: {value}. "
                f"max: {self._max_value} | min: {self._min_value}"
            ))

        return value


class StringProperty(BaseProperty):
    def __init__(
        self,
        *,
        min_length: 'Optional[int]'=None,
        max_length: 'Optional[int]'=None,
        required: 'bool'=False,
        default: 'Optional[Union[bool, int]]'=None,
        choices: 'Optional[Union[List, Tuple, Dict, Set]]'=None,
        validation: 'Optional[Callable[[bool], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        if min_length is not None and not isinstance(min_length, int):
            raise Exception()

        if max_length is not None and not isinstance(max_length, int):
            raise Exception()

        super().__init__(
            required=required,
            default=default,
            choices=choices,
            validation=validation,
            _prop_name=_prop_name,
        )
        self._min_len = min_length
        self._max_len = max_length

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        if self._choices and value not in self._choices:
            raise ValueError(f"'{value}' is not in choices ({self.choices})")

        if self._choices and isinstance(self._choices, dict) and value in self._choices:
            value = self.choices[value]

        if not isinstance(value, str):
            raise ValueError(f"'{self._property_name}' must be a 'bool'")

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        if ((self._min_len is not None and len(value) < self._min_len) or
            (self._max_len is not None and len(value) > self._max_len)):
            raise Exception((
                f"'{self._property_name}' out of defined range: {value}. "
                f"max: {self._max_len} | min: {self._min_len}"
            ))

        return value


class ListProperty(BaseProperty):
    def __init__(
        self,
        *,
        min_length: 'Optional[int]'=None,
        max_length: 'Optional[int]'=None,
        required: 'bool'=False,
        default: 'Optional[Callable[[], List[Any]]]'=None,
        validation: 'Optional[Callable[[Union[List, Set, Tuple]], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        if min_length is not None and not isinstance(min_length, int):
            raise Exception()

        if max_length is not None and not isinstance(max_length, int):
            raise Exception()

        super().__init__(
            required=required,
            default=default,
            validation=validation,
            _prop_name=_prop_name,
        )
        self._min_len = min_length
        self._max_len = max_length

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        if not isinstance(value, (list, set, tuple)):
            raise ValueError(f"'{self._property_name}' must be a 'bool'")

        value = list(value)

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        if ((self._min_len is not None and len(value) < self._min_len) or
            (self._max_len is not None and len(value) > self._max_len)):
            raise Exception((
                f"'{self._property_name}' out of defined range: {value}. "
                f"max: {self._max_len} | min: {self._min_len}"
            ))

        return value


class DictProperty(BaseProperty):
    def __init__(
        self,
        *,
        required: 'bool'=False,
        default: 'Optional[Callable[[], Dict]]'=None,
        validation: 'Optional[Callable[[Dict], bool]]'=None,
        _prop_name: 'Optional[str]' = None
    ) -> 'None':
        super().__init__(
            required=required,
            default=default,
            validation=validation,
            _prop_name=_prop_name,
        )

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError("Required property.")

        if value is None and not self._is_required:
            return

        if not isinstance(value, dict):
            raise ValueError(f"'{self._property_name}' must be a 'bool'")

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        return value
