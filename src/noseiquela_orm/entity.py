from typing import TYPE_CHECKING

from .client import DatastoreClient
from .query import Query
from .properties import BaseProperty
from .key import KeyProperty
from .utils.case_style import CaseStyle

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Tuple
    from google.cloud.datastore.entity import Entity as GoogleEntity
    from .key import ParentKey


class ModelMetaClass(type):
    def __init__(self, name: 'str', bases: 'Tuple', attrs: 'Dict') -> 'None':
        super().__init__(name, bases, attrs)

        self.kind: 'str' = attrs.get("__kind__") or name

        self.__process_meta_class(attrs)
        self.__define_datastore_client()
        self.__define_properties_case_style(attrs)
        self.__mount_query_obj()

        self._partial_key = KeyProperty(
            entity_kind=self.kind,
            project=self.project,
            namespace=self.namespace
        )

        self.__mount_property_types_validation(attrs)
        self.__handle_required_properties(attrs)
        self.__preload_properties_with_default_value(attrs)
        self.__handle_parent_key(attrs)

        self._entity_properties: 'List[str]' = list(self._entity_types.keys())
        self._data: 'Dict[str, Any]' = {
            key: value
            for key, value in self._defaults.items()
        }

    @property
    def project(self) -> 'str':
        return self._client.project

    @property
    def namespace(self) -> 'str':
        return self._client.namespace

    def __process_meta_class(self, attrs: 'Dict') -> 'None':
        client_args = (
            "project",
            "namespace",
            "credentials",
            "client_info",
            "client_options",
            "_http",
            "_use_grpc"
        )

        meta_class: 'Optional[type]' = (
            _meta if (_meta := attrs.get("Meta")) and isinstance(_meta, type)
            else None
        )

        get_from_meta = lambda arg: (
            getattr(meta_class, arg, None)
            if meta_class else None
        )

        self._allow_inheritance: 'Optional[bool]' = get_from_meta('allow_inheritance') # WIP

        self.__ds_client_args: 'Dict[str, Any]' = {
            arg: meta_attr
            for arg in client_args
            if ((meta_attr := get_from_meta(arg)) is not None)
        } if meta_class else {}

    def __define_datastore_client(self) -> 'None':
        self._client = DatastoreClient(
            **self.__ds_client_args
        )

    def __define_properties_case_style(self, attrs: 'Dict') -> 'None':
        case_style: 'Dict[str, str]' = attrs.get("__case_style__") or {}
        self._convert_property_name = CaseStyle(
            from_case=case_style.get("from") or "snake_case",
            to_case=case_style.get("to") or "camel_case",
        )

    def __mount_query_obj(self) -> 'None':
        self.query = Query(
            partial_query=self._client.get_partial_query(
                kind=self.kind
            ),
            entity_instance=self
        )

    def __mount_property_types_validation(self, attrs: 'Dict') -> 'None':
        self._entity_types: 'Dict[str, Callable]' = {
            key: value._validate
            for key, value in attrs.items()
            if isinstance(value, BaseProperty)
        }

        self._entity_types.update({
            "id": self._partial_key._validate
        })

    def __handle_required_properties(self, attrs: 'Dict') -> 'None':
        self._required: 'List[str]' = [
            key for key, value in attrs.items()
            if (isinstance(value, BaseProperty) and
                value.required)
        ]

    def __preload_properties_with_default_value(self, attrs: 'Dict') -> 'None':
        self._defaults: 'Dict[str, Any]' = {
            key: value.default_value
            for key, value in attrs.items()
            if (isinstance(value, BaseProperty) and
                value.default_value is not None)
        }

        self._defaults.update({
            "id": None
        })

    def __handle_parent_key(self, attrs: 'Dict') -> 'None':
        self._parent_entity: 'Optional[ParentKey]' = attrs.get("__parent__") or None

        if not self._parent_entity:
            return

        self._required.append("parent_id")
        self._entity_types.update({
            "parent_id": self._parent_entity._validate
        })
        self._defaults.update({
            "parent_id": None
        })


class Model(metaclass=ModelMetaClass):
    def __init__(self, **kwargs) -> 'None':
        self._data = {
            key: value
            for key, value in kwargs.items()
        }

    def __getattribute__(self, key: 'str') -> 'Any':
        data = super().__getattribute__("_data")
        if key in data:
            return data[key]
        if key in super().__getattribute__("_entity_types"):
            return
        return super().__getattribute__(key)

    def __setattr__(self, key: 'str', value: 'Any') -> 'None':
        if key in super().__getattribute__("_entity_types"):
            self._data[key] = self._entity_types[key](value)
        else:
            super().__setattr__(key, value)

    def save(self) -> 'None':
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
            entity=self._client.mount_google_entity_from_dict(
                entity,
                self._convert_property_name
            )
        )

    @classmethod
    def _mount_from_google_entity(cls, entity: 'GoogleEntity') -> 'Model':
        properties = cls._entity_properties
        properties_to_mount = set(properties) - set(["id", "parent_id"])

        model_args = {"id": entity.key.id}

        if "parent_id" in properties:
            model_args["parent_id"] = entity.key.parent.id

        for property in properties_to_mount:
            model_args[property] = entity.get(
                cls._convert_property_name(property)
            )
        return cls(**model_args)

    def to_dict(self) -> 'Dict[str, Any]':
        return {
            field: getattr(self, field)
            for field in self._data.keys()
            if field in self._entity_properties
        }

    def __repr__(self) -> 'str':
        return (
            f"<{self.__class__.__name__} - id: {self.id}>"
        )
