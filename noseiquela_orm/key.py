from typing import TYPE_CHECKING

from google.cloud.datastore.key import Key as GoogleEntityKey

if TYPE_CHECKING:
    from typing import Optional, Union


class BaseKey:
    def __init__(self, project: 'str', namespace: 'str') -> 'None':
        self.project = project
        self.namespace = namespace
        self._supported_types_map = {
            str: lambda x: x,
            int: lambda x: x,
        }

    def _validate(self, value: 'Union[str, int]') -> 'Union[str, int]':
        _supported_types = tuple(self._supported_types_map.keys())
        if not isinstance(value, _supported_types):
            raise

        return value

    def get_complete_key(self, id_or_name: 'Union[str, int]') -> 'GoogleEntityKey':
        return self._partial_key.completed_key(id_or_name)

    def _mount_partial_key(
        self,
        parent_key: 'Optional[GoogleEntityKey]'=None
    ) -> 'GoogleEntityKey':
        return GoogleEntityKey(
            self.kind,
            project=self.project,
            namespace=self.namespace,
            parent=parent_key
        )


class KeyProperty(BaseKey):
    def __init__(
        self,
        entity_kind: 'str',
        project: 'Optional[str]'=None,
        namespace: 'Optional[str]'=None
    ) -> 'None':
        super().__init__(project=project, namespace=namespace)
        self.kind = entity_kind


class ParentKey(BaseKey):
    def __init__(
        self,
        parent,
        project: 'str'=None,
        namespace: 'str'=None,
        required: 'bool'=False # WIP
    ) -> 'None':
        self._parent_entity = parent
        project = project or self._parent_entity.project
        namespace = namespace or self._parent_entity.namespace
        super().__init__(project=project, namespace=namespace)

    @property
    def kind(self) -> 'str':
        return self._parent_entity.kind
