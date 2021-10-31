from typing import Any, Callable, Iterable, Optional, Union
from datetime import datetime
from proto.datetime_helpers import DatetimeWithNanoseconds
from google.cloud.datastore.key import Key as GoogleEntityKey

from decimal import Decimal
from json import dumps
from dateutil.parser import parse


class BaseField:
    def __init__(
        self,
        db_field: Optional[str]=None,
        required: bool=False,
        default: Optional[Any]=None,
        choices: Optional[Iterable]=None,
        validation: Optional[Callable]=None,
        parse_value: bool=True
    ) -> None:
        self.db_field = db_field
        self.required = required
        self.default_value = default
        self.choices = choices
        self.validation = validation
        self.parse_value = parse_value

    def _validate(self, value: Any) -> Any:
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


class BooleanField(BaseField):
    truthy = ["True", "true", 1, "1", "yes"]
    falsy = ["False", "false", 0, "0", "no"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_type = bool
        self._supported_types_map = {
            str: self._to_bool,
            int: self._to_bool,
            bool: lambda x: x
        }

    def _to_bool(self, value):
        if value in self.truthy:
            return True
        elif value in self.falsy:
            return False
        return bool(value)


class DateTimeField(BaseField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_type = datetime
        self._supported_types_map = {
            str: parse,
            datetime: lambda x: x,
            DatetimeWithNanoseconds: lambda x: parse(x.isoformat())
        }


class FloatField(BaseField):
    def __init__(self, force_string=False, min=None, max=None, *args, **kwargs) -> None:
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


class IntegerField(BaseField):
    def __init__(self, min=None, max=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._min_value = min
        self._max_value = max
        self._default_type = int
        self._supported_types_map = {
            int: lambda x: x,
            str: int,
            float: int
        }


class StringField(BaseField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_type = str
        self._supported_types_map = {
            str: lambda x: x,
            int: str,
            float: str,
            list: dumps,
            dict: dumps,
        }


class ListField(BaseField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_type = list
        self._supported_types_map = {
            list: lambda x: x
        }


class DictField(BaseField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._default_type = dict
        self._supported_types_map = {
            dict: lambda x: x
        }


class BaseKey:
    def __init__(self, project, namespace) -> None:
        self.project = project
        self.namespace = namespace
        self._supported_types_map = {
            str: lambda x: x,
            int: lambda x: x,
        }

    def _validate(self, value: Union[str, int]) -> Union[str, int]:
        _supported_types = tuple(self._supported_types_map.keys())
        if not isinstance(value, _supported_types):
            raise

        return value

    def get_complete_key(self, id_or_name):
        return self._partial_key.completed_key(id_or_name)

    def _mount_partial_key(self, parent_key=None):
        return GoogleEntityKey(
            self.kind,
            project=self.project,
            namespace=self.namespace,
            parent=parent_key
        )


class KeyField(BaseKey):
    def __init__(self, entity_kind, project=None, namespace=None) -> None:
        super().__init__(project=project, namespace=namespace)
        self.kind = entity_kind


class ParentKey(BaseKey):
    def __init__(self, parent, project=None, namespace=None, required=False) -> None:
        self._parent_entity = parent
        project = project or self._parent_entity._project
        namespace = namespace or self._parent_entity._namespace
        super().__init__(project=project, namespace=namespace)

    @property
    def kind(self):
        return self._parent_entity.kind
