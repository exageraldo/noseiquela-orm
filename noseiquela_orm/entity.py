from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING
from google.cloud.datastore.entity import Model as GoogleEntity

from .client import DataStoreClient
from .query import Query
from .properties import BaseProperty, BaseKey, KeyProperty
from .utils.case_style import CaseStyle

if TYPE_CHECKING:
    from .properties import ParentKey


class ModelMetaClass(type):
    def __init__(self, name: str, bases: Tuple, attrs: Dict) -> None:
        super().__init__(name, bases, attrs)

        self.kind: str = attrs.get("__kind__") or name

        self._process_meta(attrs)
        self._define_datastore_client()
        self._define_case_style(attrs)
        self._mount_query()

        self._partial_key = KeyProperty(
            entity_kind=self.kind,
            project=self.project,
            namespace=self.namespace
        )

        self._handle_properties_validation(attrs)
        self._handle_required_properties(attrs)
        self._handle_properties_default_value(attrs)
        self._handle_parent_key(attrs)

        self._entity_properties: List[str] = list(self._entity_types.keys())

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

    def _handle_parent_key(self, attrs: Dict) -> None:
        self._parent_entity: Optional['ParentKey'] = attrs.get("__parent__")

        if self._parent_entity:
            self._required.append("parent_id")
            self._entity_types.update({
                "parent_id": self._parent_entity._validate
            })
            self._defaults.update({
                "parent_id": None
            })

    def _handle_properties_default_value(self, attrs: Dict) -> None:
        self._defaults: Dict[str, Any] = {
            key: value.default_value
            for key, value in attrs.items()
            if (isinstance(value, BaseProperty) and
                value.default_value is not None)
        }

        self._defaults.update({
            "id": None
        })

    def _handle_properties_validation(self, attrs: Dict) -> None:
        self._entity_types: Dict[str, Callable] = {
            key: value._validate
            for key, value in attrs.items()
            if isinstance(value, BaseProperty)
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

    def _handle_required_properties(self, attrs: Dict) -> None:
        self._required: List[str] = [
            key for key, value in attrs.items()
            if (isinstance(value, BaseProperty) and
                value.required)
        ]

    def _define_case_style(self, attrs: Dict) -> None:
        _case_style: Dict[str, str] = attrs.get("__case_style__") or {}
        self._convert_property_name = CaseStyle(
            from_case=_case_style.get("from") or "snake_case",
            to_case=_case_style.get("to") or "camel_case",
        )

    def _process_meta(self, attrs: Dict) -> None:
        _client_args = (
            "project",
            "namespace",
            "credentials",
            "client_info",
            "client_options",
            "_http",
            "_use_grpc"
        )

        meta_class: Optional[type] = (
            _meta if (_meta := attrs.get("Meta")) and isinstance(_meta, type)
            else None
        )

        self._client_args: Dict[str, Any] = {
            arg: meta_attr
            for arg in _client_args
            if ((meta_attr := getattr(meta_class, arg, None)) is not None)
        } if meta_class else {}


class Model(metaclass=ModelMetaClass):
    def __init__(self, **kwargs) -> None:
        self._data: Dict[str, Any] = {
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

    def save(self) -> None:
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            field: getattr(self, field)
            for field in self._data.keys()
            if field in self._entity_properties
        }

    @classmethod
    def _create_from_google_entity(cls, entity: GoogleEntity) -> "Model":
        _properties = cls._entity_properties
        _properties_to_mount = set(_properties) - set(["id", "parent_id"])

        instance = cls()
        setattr(instance, "id", entity.key.id)

        if "parent_id" in _properties:
            setattr(instance, "parent_id", entity.key.parent.id)

        for property in _properties_to_mount:
            setattr(instance, property, entity.get(
                cls._convert_property_name(property)
            ))
        return instance

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} - id: {self.id}>"
        )
