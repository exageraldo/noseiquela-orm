from typing import Any
from google.cloud.datastore.entity import Entity as GoogleEntity

from .client import DataStoreClient
from .query import Query
from .fields import BaseField, BaseKey, KeyField


class EntityMetaClass(type):
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        self.kind = attrs.get("__kind__") or name
        self._parent_entity = attrs.get("__parent__")
        self._project = attrs.get("__project__") or self._client.project
        self._namespace = attrs.get("__namespace__") or self._client.namespace

        self.query = Query(
            partial_query=self._client._get_partial_query(
                kind=self.kind
            ),
            entity_instance=self
        )

        self._partial_key = KeyField(
            entity_kind=self.kind,
            project=self._project,
            namespace=self._namespace
        )

        self._entity_types = {
            key: value._validate
            for key, value in attrs.items()
            if isinstance(value, BaseField)
        }

        self._entity_types.update({
            "id": self._partial_key._validate
        })

        self._required = [
            key for key, value in attrs.items()
            if (isinstance(value, BaseField) and
                value.required)
        ]

        self._defaults = {
            key: value.default_value
            for key, value in attrs.items()
            if (isinstance(value, BaseField) and
                value.default_value is not None)
        }

        self._defaults.update({
            "id": None
        })

        if self._parent_entity:
            self._required.append("parent_id")
            self._entity_types.update({
                "parent_id": self._parent_entity._validate
            })
            self._defaults.update({
                "parent_id": None
            })

        self._entity_fields = list(self._entity_types.keys())


class Entity(metaclass=EntityMetaClass):
    _client = DataStoreClient()

    def __init__(self, **kwargs):
        self._data = {
            "id": None
        }

        for key, default_value in self._defaults.items():
            self._data[key] = default_value

        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key: str) -> Any:
        _data = super().__getattribute__("_data")
        if key in _data:
            return _data[key]
        if key in super().__getattribute__("_entity_types"):
            return
        return super().__getattribute__(key)

    def __setattr__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)
        if key in super().__getattribute__("_entity_types"):
            self._data[key] = self._entity_types[key](value)

    @staticmethod
    def _to_camel_case(key: str) -> str:
        splited_key = key.split('_')
        return splited_key[0] + ''.join(
            [x.title() for x in splited_key[1:]]
        )

    def save(self):
        for required_property in self._required:
            if self._data[required_property] is None:
                raise

        entity = self.to_dict()
        parent_key = None
        if "parent_id" in entity.keys():
            partial_parent_key = self._parent_entity._mount_partial_key()
            parent_key = partial_parent_key.completed_key(
                entity["parent_id"]
            )

        entity_partial_key = self._partial_key._mount_partial_key(
            parent_key=parent_key
        )

        if entity["id"] is not None:
            entity["id"] = entity_partial_key.completed_key(entity["id"])
        else:
            entity["id"] = entity_partial_key

        if "parent_id" in entity.keys():
            del entity["parent_id"]

        self.id = self._client.save(entity=entity)

    def to_dict(self):
        return {
            field: getattr(self, field)
            for field in self._data.keys()
            if field in self._entity_fields
        }

    @classmethod
    def _create_from_google_entity(cls, entity: GoogleEntity) -> "Entity":
        _fields = cls._entity_fields
        _fields_to_mount = set(cls._entity_fields) - set(["id", "parent_id"])

        instance = cls()
        setattr(instance, "id", entity.key.id)

        if "parent_id" in _fields:
            setattr(instance, "parent_id", entity.key.parent.id)

        for field in _fields_to_mount:
            setattr(instance, field, entity.get(cls._to_camel_case(field)))

        return instance

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} - id: {self.id}>"
        )
