from typing import Any, Callable, Dict
from google.cloud.datastore.entity import Entity as GoogleEntity

from .client import DataStoreClient
from .query import Query
from .fields import BaseField, BaseKey, KeyField
from .utils.case_style import CaseStyle


class EntityMetaClass(type):
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        self.kind = attrs.get("__kind__") or name

        self._process_meta(attrs)
        self._define_datastore_client()
        self._define_case_style(attrs)
        self._mount_query()

        self._partial_key = KeyField(
            entity_kind=self.kind,
            project=self.project,
            namespace=self.namespace
        )

        self._handle_properties_validation(attrs)
        self._handle_required_properties(attrs)
        self._handle_properties_default_value(attrs)
        self._handle_parent_key(attrs)

        self._entity_fields = list(self._entity_types.keys())

    @property
    def project(self) -> str:
        return self._client.project

    @property
    def namespace(self) -> str:
        return self._client.namespace

    def _define_datastore_client(self) -> None:
        self._client = DataStoreClient(
            **self._client_args
        )

    def _handle_parent_key(self, attrs) -> None:
        self._parent_entity = attrs.get("__parent__")

        if self._parent_entity:
            self._required.append("parent_id")
            self._entity_types.update({
                "parent_id": self._parent_entity._validate
            })
            self._defaults.update({
                "parent_id": None
            })

    def _handle_properties_default_value(self, attrs) -> None:
        self._defaults = {
            key: value.default_value
            for key, value in attrs.items()
            if (isinstance(value, BaseField) and
                value.default_value is not None)
        }

        self._defaults.update({
            "id": None
        })

    def _handle_properties_validation(self, attrs) -> None:
        self._entity_types = {
            key: value._validate
            for key, value in attrs.items()
            if isinstance(value, BaseField)
        }

        self._entity_types.update({
            "id": self._partial_key._validate
        })

    def _mount_query(self) -> None:
        self.query = Query(
            partial_query=self._client._get_partial_query(
                kind=self.kind
            ),
            entity_instance=self
        )

    def _handle_required_properties(self, attrs) -> None:
        self._required = [
            key for key, value in attrs.items()
            if (isinstance(value, BaseField) and
                value.required)
        ]

    def _define_case_style(self, attrs) -> None:
        _case_style = attrs.get("__case_style__") or {}
        self._convert_property_name = CaseStyle(
            from_case=_case_style.get("from") or "snake_case",
            to_case=_case_style.get("to") or "camel_case",
        )

    def _process_meta(self, attrs) -> None:
        _client_args = (
            "project",
            "namespace",
            "credentials",
            "client_info",
            "client_options",
            "_http",
            "_use_grpc"
        )

        meta_class = attrs.get("Meta")

        self._client_args = {
            arg: meta_attr
            for arg in _client_args
            if ((meta_attr := getattr(meta_class, arg, None)) is not None)
        } if isinstance(meta_class, type) else {}


class Entity(metaclass=EntityMetaClass):
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

        self.id = self._client.save(
            entity=self._client._mount_google_entity(
                entity,
                self._convert_property_name
            )
        )

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
            setattr(instance, field, entity.get(
                cls._convert_property_name(field)
            ))
        return instance

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} - id: {self.id}>"
        )
