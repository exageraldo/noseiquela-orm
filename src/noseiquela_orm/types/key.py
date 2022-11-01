from typing import TYPE_CHECKING

from .base import BaseProperty

if TYPE_CHECKING:
    from typing import (
        Optional, Union, Any, Callable, Tuple, Set, Dict, List
    )

    from google.cloud.datastore.key import Key as GKey

    from ..entity import Model # type: ignore


class KeyProperty(BaseProperty):
    def __init__(
        self,
        *,
        parent: 'Union[str, Model]'=False,
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
        self._parent = parent

    def __set_name__(self, owner_class: 'Model', name: 'str'):
        super().__set_name__(owner_class, name)

        def _partial_g_key(
            parent: 'Optional[GKey]'=None
        ):
            if parent and parent.is_partial:
                raise ValueError("'parent' must be a complete key.")

            return owner_class._client.mount_partial_g_key(
                kind=owner_class.kind,
                parent=parent,
            )

        def _complete_g_key(
            id_or_name: 'Union[str, int]',
            parent: 'Optional[GKey]'=None,
        ):
            if parent and parent.is_partial:
                raise ValueError("'parent' must be a complete key.")

            return owner_class._client.mount_complete_g_key(
                kind=owner_class.kind,
                id_or_name=id_or_name,
                parent=parent,
            )

        owner_class._partial_g_key = staticmethod(_partial_g_key)
        owner_class._complete_g_key = staticmethod(_complete_g_key)

        if not self._parent:
            return

        self._parent: 'Model' = ( # type: ignore
            owner_class._model_registry[self._parent]
            if isinstance(self._parent, str)
            else self._parent
        )

        def _parent_complete_g_key(
            id_or_name: 'Union[str, int]',
        ) -> 'GKey':
            return self._parent._client.mount_complete_g_key( # type: ignore
                kind=self._parent.kind, # type: ignore
                id_or_name=id_or_name,
            )

        owner_class._parent_complete_g_key = staticmethod(_parent_complete_g_key)

        owner_class.parent_id = self.__class__(required=True)
        owner_class.parent_id._property = self._property
        owner_class.parent_id._property_name = "parent_id"

    def _parse_and_validate(self, value) -> 'Any':
        if value is None and self._is_required:
            raise ValueError(f"'{self._property_name}'is required.")

        if value is None and not self._is_required:
            return

        if self._choices and value not in self._choices:
            raise ValueError(f"'{value}' is not in choices ({self.choices})")

        if self._choices and isinstance(self._choices, dict) and value in self._choices:
            value = self.choices[value]

        if not isinstance(value, (int, str)):
            raise ValueError(f"'{self._property_name}' must be a 'str' or 'int")

        if self._validation and not self._validation(value):
            raise ValueError(f"'{value}' did not pass validation.")

        return value

