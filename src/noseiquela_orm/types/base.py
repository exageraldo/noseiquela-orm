from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Optional, Union, Any, Callable, Tuple, Set, Dict, List
    )


class BaseProperty(ABC):
    def __init__(
        self,
        *, # keyword-only
        required: 'bool'=False,
        default: 'Optional[Any]'=None,
        choices: 'Optional[Union[List, Tuple, Dict, Set]]'=None,
        validation: 'Optional[Callable[[Any], bool]]'=None,
        _prop_name: 'Optional[str]'=None,
    ) -> 'None':
        if choices and not isinstance(choices, (list, tuple, dict, set)):
            raise Exception("'choices' must be a list, tuple, dict or set.")

        if validation and not callable(validation):
            raise Exception("'validation' must be a callable.")

        self._is_required = required
        self._choices = choices
        self._validation = validation
        self._custom_prop_name = _prop_name
        self._default_value = default

    def __set_name__(self, owner_class, name):
        self._property = owner_class
        self._property_name = name

    def __set__(self, owner_instance, value):
        value = self._parse_and_validate(value)
        owner_instance.__dict__[self._property_name] = value

    def __get__(self, owner_instance, owner_class):
        if owner_instance is None:
            return self

        return owner_instance.__dict__.get(
            self._property_name
        )

    def _generate_default_value(self):
        return None if self._default_value is None else (
            self._default_value
            if not callable(self._default_value)
            else self._default_value()
        )

    @abstractmethod
    def _parse_and_validate(self, value) -> 'Any':
        ...
