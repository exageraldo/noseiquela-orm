from datetime import datetime
from decimal import Decimal
from json import dumps
from typing import TYPE_CHECKING

from dateutil.parser import parse
from proto.datetime_helpers import DatetimeWithNanoseconds

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable, Optional



class BaseProperty:
    def __init__(
        self,
        db_field: 'Optional[str]'=None,
        required: 'bool'=False,
        default: 'Optional[Any]'=None,
        choices: 'Optional[Iterable]'=None,
        validation: 'Optional[Callable]'=None,
        parse_value: 'bool'=True
    ) -> 'None':
        self.db_field = db_field
        self.required = required
        self.default_value = default
        self.choices = choices
        self.validation = validation
        self.parse_value = parse_value

    def _validate(self, value: 'Any') -> 'Any':
        value = self.default_value if value is None else value
        if not value and not self.required:
            return

        _supported_types = tuple(self._supported_types_map.keys())
        if not isinstance(value, _supported_types):
            raise

        parser_func = self._supported_types_map[type(value)]
        type_func = self._supported_types_map[self._default_type]
        converted_value = parser_func(value) if self.parse_value else type_func(value)

        if self.validation and not self.validation(converted_value):
            raise

        if self.choices and converted_value not in self.choices:
            raise

        return converted_value


class BooleanProperty(BaseProperty):
    truthy = ["True", "true", 1, "1", "yes"]
    falsy = ["False", "false", 0, "0", "no"]

    def __init__(self, *args, **kwargs) -> 'None':
        super().__init__(*args, **kwargs)
        self._default_type = bool
        self._supported_types_map = {
            str: self._to_bool,
            int: self._to_bool,
            bool: lambda x: x
        }

    def _to_bool(self, value: 'Any') -> 'bool':
        if value in self.truthy:
            return True
        elif value in self.falsy:
            return False
        return bool(value)


class DateTimeProperty(BaseProperty):
    def __init__(self, *args, **kwargs) -> 'None':
        super().__init__(*args, **kwargs)
        self._default_type = datetime
        self._supported_types_map = {
            str: parse,
            datetime: lambda x: x,
            DatetimeWithNanoseconds: lambda x: parse(x.isoformat())
        }


class FloatProperty(BaseProperty):
    def __init__(
        self,
        force_string: 'bool'=False,
        min: 'Optional[float]'=None,
        max: 'Optional[float]'=None,
        *args,
        **kwargs
    ) -> 'None':
        super().__init__(*args, **kwargs)
        self._force_string = force_string
        self._min_value = min
        self._max_value = max
        self._default_type = str if force_string else float
        self._supported_types_map = {
            str: Decimal,
            float: Decimal,
            int: Decimal,
            Decimal: lambda x: x
        }


class IntegerProperty(BaseProperty):
    def __init__(
        self,
        min: 'Optional[int]'=None,
        max: 'Optional[int]'=None,
        *args,
        **kwargs
    ) -> 'None':
        super().__init__(*args, **kwargs)
        self._min_value = min
        self._max_value = max
        self._default_type = int
        self._supported_types_map = {
            int: lambda x: x,
            str: int,
            float: int
        }


class StringProperty(BaseProperty):
    def __init__(self, *args, **kwargs) -> 'None':
        super().__init__(*args, **kwargs)
        self._default_type = str
        self._supported_types_map = {
            str: lambda x: x,
            int: str,
            float: str,
            list: dumps,
            dict: dumps,
        }


class ListProperty(BaseProperty):
    def __init__(self, *args, **kwargs) -> 'None':
        super().__init__(*args, **kwargs)
        self._default_type = list
        self._supported_types_map = {
            list: lambda x: x
        }


class DictProperty(BaseProperty):
    def __init__(self, *args, **kwargs) -> 'None':
        super().__init__(*args, **kwargs)
        self._default_type = dict
        self._supported_types_map = {
            dict: lambda x: x
        }
