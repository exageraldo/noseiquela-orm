import inspect
from typing import TYPE_CHECKING

from .query import Query
from .types.properties import BaseProperty
from .utils.case_style import CaseStyle
from .utils.collections import merge_dicts

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Tuple, Union

    from google.cloud.datastore.entity import Entity as GEntity
    from google.cloud.datastore.key import Key as GKey


class ModelMeta(type):
    def __new__(cls, name: 'str', bases: 'Tuple', attrs: 'Dict'):
        attrs["kind"] = attrs.pop("__kind__", name)

        if "id" not in attrs:
            from .types.key import KeyProperty
            attrs["id"] = KeyProperty()

        meta_class = None
        if "Meta" in attrs and inspect.isclass((attrs["Meta"])):
            meta_class = attrs.pop("Meta")

        ds_client_args = (
            {} if meta_class is None
            else cls.__get_client_args_from_meta(meta_class)
        )

        from .client import DatastoreClient
        ds_client = DatastoreClient(**ds_client_args)

        attrs['_client'] = ds_client
        attrs['project'] = ds_client.project
        attrs['namespace'] = ds_client.namespace

        case_style = merge_dicts(
            {
                "from_case": "snake_case",
                "to_case": "snake_case",
            },
            attrs.pop("__case_style__", {})
        )

        attrs['_case_style'] = CaseStyle(**case_style)

        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def __get_client_args_from_meta(cls, meta_class: 'type') -> 'Dict[str, Any]':
        client_args = (
            "project",
            "namespace",
            "credentials",
            "client_info",
            "client_options",
            "_http",
            "_use_grpc"
        )

        return {
            arg: meta_attr
            for arg in client_args
            if ((meta_attr:=getattr(meta_class, arg, None)) is not None)
        }


class Model(metaclass=ModelMeta):
    _model_registry: 'Dict[str, Model]' = {}

    def __init__(self, **kwargs) -> None:
        unmapped_props = set(kwargs.keys()) - set(self._all_props) # type: ignore

        if unmapped_props:
            raise AttributeError((
                f"type object '{self.__class__.__name__}' "
                f"has no attributes: {', '.join(unmapped_props)}."
            ))

        data = merge_dicts(
            self._generate_default_dict(),
            kwargs
        )

        for prop, value in data.items():
            setattr(self, prop, value)

    def __init_subclass__(cls):
        cls._model_registry[cls.__name__] = cls

        _all_props = getattr(cls, "_all_props", [])
        _default_props = getattr(cls, "_default_props", {})
        _required_props = getattr(cls, "_required_props", [])

        for prop_name, prop in vars(cls).items():
            if not isinstance(prop, BaseProperty):
                continue

            _all_props.append(prop_name)

            if prop._is_required:
                _required_props.append(prop_name)

            if prop._default_value is not None:
                default = prop._generate_default_value
                _default_props[prop._property_name] = default


        setattr(cls, "_all_props", _all_props)
        setattr(cls, "_default_props", _default_props)
        setattr(cls, "_required_props", _required_props)
        setattr(cls, "query", Query(
            partial_query=cls._client.get_partial_query(
                kind=cls.kind
            )
        ))

    def __setattr__(self, key: 'str', value: 'Any') -> 'None':
        if key not in self._all_props: # type: ignore
            raise AttributeError((
                f"type object '{self.__class__.__name__}' "
                f"has no attribute: {key}."
            ))
        super().__setattr__(key, value)

    def _mount_entity_g_key(self) -> 'GKey':
        has_parent = hasattr(self, "parent_id")
        if has_parent and not self.parent_id: # type: ignore
            raise ValueError((
                "'parent_id' must be a valid 'str' or 'int' "
                "to mount the key (partial or complete)."
            ))

        parent_key = (
            self._parent_complete_g_key(self.parent_id) # type: ignore
            if has_parent
            else None
        )

        if self.id is None:
            return self._partial_g_key(parent_key) # type: ignore
        return self._complete_g_key(self.id, parent_key) # type: ignore

    @classmethod
    def _generate_default_dict(cls) -> 'Dict[str, Any]':
        return {
            prop: gen_default()
            for prop, gen_default in cls._default_props.items() # type: ignore
        }

    @classmethod
    def _mount_from_google_entity(cls, entity: 'GEntity') -> 'Model':
        data = merge_dicts(
            cls._generate_default_dict(),
            {"id": entity.key.id_or_name}
        )

        if hasattr(cls, "parent_id") and entity.key.parent:
            data["parent_id"] = entity.key.parent.id_or_name

        props_to_mount = [
            prop for prop in cls._all_props # type: ignore
            if prop not in ["id"]
        ]

        for property in props_to_mount:
            data[property] = entity.get(
                cls._case_style.revert(property) # type: ignore
            )
        return cls(**data)

    def as_dict(self) -> 'Dict[str, Any]':
        has_parent = hasattr(self, "parent_id")
        base_dict = {
            "id": None,
            "parent_id": None,
        } if has_parent else {"id": None}

        return merge_dicts(
            base_dict,
            {
                prop_name: value
                for prop_name, value in vars(self).items()
                if prop_name in self._all_props # type: ignore
            }
        )

    def as_entity(self) -> 'GEntity':
        data = self.as_dict()

        _ = data.pop("id", None)
        _ = data.pop("parent_id", None)

        from google.cloud.datastore.entity import Entity
        entity = Entity(key=self._mount_entity_g_key())

        entity.update({
            self._case_style(prop_name): value # type: ignore
            for prop_name, value in data.items()
        })

        return entity

    def save(self) -> 'None':
        g_entity = self.as_entity()

        g_entity = self._client.save( # type: ignore
            entity=g_entity
        )

        self.id = g_entity.key.id

    def __repr__(self) -> 'str':
        return (
            f"<{self.__class__.__name__} - id: {self.id}>"
        )
