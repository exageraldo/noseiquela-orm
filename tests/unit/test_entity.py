import os
from unittest import mock

import pytest

from noseiquela_orm.entity import Model

from .utils import mount_entity, mount_key


def test_model_base_with_default_kind():
    class ModelSample(Model):
        ...

    assert ModelSample.kind == "ModelSample"
    assert ModelSample._client.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample._client.namespace is None


def test_model_base_with_custom_kind():
    class ModelSample(Model):
        __kind__ = "model_sample"

    assert ModelSample.kind == "model_sample"
    assert ModelSample._client.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample._client.namespace is None


def test_model_base_with_meta_info():
    class ModelSample(Model):
        class Meta:
            project = "other-project"
            namespace = "custom-namespace"

    assert ModelSample._client.project == "other-project"
    assert ModelSample._client.namespace == "custom-namespace"


def test_model_base_with_default_case_style():
    class ModelSample(Model):
        ...

    assert ModelSample._case_style.from_case == "snake_case"
    assert ModelSample._case_style.to_case == "snake_case"


@pytest.mark.parametrize(
    "case_style,from_case,to_case",
    [
        pytest.param(
            {"to_case": "camel_case"},
            "snake_case",
            "camel_case",
            id='from-snake-to-camel'
        ),
        pytest.param(
            {"from_case": "camel_case"},
            "camel_case",
            "snake_case",
            id='from-camel-to-snake'
        ),
        pytest.param(
            {"from_case": "camel_case", "to_case": "camel_case"},
            "camel_case",
            "camel_case",
            id='from-camel-to-camel'
        ),
    ],
)
def test_model_base_with_custom_case_style(case_style, from_case, to_case):
    class ModelSample(Model):
        __case_style__ = case_style

    assert ModelSample._case_style.from_case == from_case
    assert ModelSample._case_style.to_case == to_case


def test_model_base_query():
    from noseiquela_orm.query import Query
    from google.cloud.datastore.query import Query as GQuery

    class ModelSample(Model):
        ...

    partial_query = ModelSample.query.partial_query()

    assert isinstance(ModelSample.query, Query)
    assert isinstance(partial_query, GQuery)
    assert ModelSample.query.entity_instance == ModelSample
    assert ModelSample.query.partial_query.keywords == {"kind": "ModelSample"}
    assert ModelSample.project == partial_query.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample.namespace == partial_query.namespace == None


def test_model_base_partial_key_with_no_defined_id():
    from noseiquela_orm.types.key import KeyProperty
    from google.cloud.datastore.key import Key as GKey

    class ModelSample(Model):
        ...

    g_key = ModelSample._partial_g_key()

    assert isinstance(ModelSample.id, KeyProperty)
    assert ModelSample.id._is_required is False # by default
    assert isinstance(g_key, GKey)
    assert g_key.parent is None
    assert not hasattr(ModelSample, "parent_id")
    assert ModelSample.kind == g_key.kind
    assert ModelSample.project == g_key.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample.namespace == g_key.namespace == None


def test_model_base_partial_key_with_defined_id_and_no_parent():
    from noseiquela_orm.types.key import KeyProperty
    from google.cloud.datastore.key import Key as GKey

    class ModelSample(Model):
        id = KeyProperty(required=True)

    g_key = ModelSample._partial_g_key()

    assert isinstance(ModelSample.id, KeyProperty)
    assert ModelSample.id._is_required is True
    assert isinstance(g_key, GKey)
    assert g_key.parent is None
    assert not hasattr(ModelSample, "parent_id")
    assert ModelSample.kind == g_key.kind
    assert ModelSample.project == g_key.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample.namespace == g_key.namespace == None


def test_model_base_partial_key_with_defined_id_and_model_parent():
    from noseiquela_orm.types.key import KeyProperty

    class ParentModel(Model):
        ...

    class ModelSample(Model):
        id = KeyProperty(parent=ParentModel)


    with pytest.raises(Exception):
        ModelSample._partial_g_key(
            parent=ParentModel._partial_g_key(),
        )

    parent_g_key_from_model = ModelSample._parent_complete_g_key(
            id_or_name=42
    )

    parent_g_key_from_parent_model = ParentModel._complete_g_key(
        id_or_name=42,
    )

    assert parent_g_key_from_model.kind == parent_g_key_from_parent_model.kind
    assert parent_g_key_from_model.id_or_name == parent_g_key_from_parent_model.id_or_name
    assert parent_g_key_from_model.project == parent_g_key_from_parent_model.project
    assert parent_g_key_from_model.namespace == parent_g_key_from_parent_model.namespace

    g_key = ModelSample._partial_g_key(
        parent=ParentModel._complete_g_key(
            id_or_name=42,
        ),
    )

    assert isinstance(ModelSample.id, KeyProperty)
    assert issubclass(ModelSample.id._parent, Model)
    assert ModelSample.id._parent == ParentModel
    assert ModelSample.kind == g_key.kind
    assert ModelSample.id._parent.kind == ParentModel.kind == g_key.parent.kind
    assert ModelSample.project == ModelSample.id._parent.project == g_key.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample.namespace == ModelSample.id._parent.namespace == g_key.namespace == None

def test_model_base_partial_key_with_defined_id_and_str_parent():
    from noseiquela_orm.types.key import KeyProperty

    class ParentModel(Model):
        ...

    class ModelSample(Model):
        id = KeyProperty(parent='ParentModel')


    with pytest.raises(Exception):
        ModelSample._partial_g_key(
            parent=ParentModel._partial_g_key(),
        )

    parent_g_key_from_model = ModelSample._parent_complete_g_key(
            id_or_name=42
    )

    parent_g_key_from_parent_model = ParentModel._complete_g_key(
        id_or_name=42,
    )

    assert parent_g_key_from_model.kind == parent_g_key_from_parent_model.kind
    assert parent_g_key_from_model.id_or_name == parent_g_key_from_parent_model.id_or_name
    assert parent_g_key_from_model.project == parent_g_key_from_parent_model.project
    assert parent_g_key_from_model.namespace == parent_g_key_from_parent_model.namespace

    g_key = ModelSample._partial_g_key(
        parent=ParentModel._complete_g_key(
            id_or_name=42,
        ),
    )

    assert isinstance(ModelSample.id, KeyProperty)
    assert issubclass(ModelSample.id._parent, Model)
    assert ModelSample.id._parent == ParentModel
    assert ModelSample.kind == g_key.kind
    assert ModelSample.id._parent.kind == ParentModel.kind == g_key.parent.kind
    assert ModelSample.project == ModelSample.id._parent.project == g_key.project == os.environ['DATASTORE_PROJECT_ID']
    assert ModelSample.namespace == ModelSample.id._parent.namespace == g_key.namespace == None



# def test_model_base_partial_key_with_custom_parent():
#     from noseiquela_orm.types.key import KeyProperty, ReferenceProperty
#     from google.cloud.datastore.key import Key as GKey

#     class ParentModel(Model):
#         ...

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(
#             ParentModel,
#             project="custom-project",
#             namespace="other-namespace"
#         )

#     part_key = ModelSample._partial_key
#     g_key = part_key._mount_partial_key()

#     assert isinstance(part_key, KeyProperty)
#     assert isinstance(g_key, GKey)
#     assert isinstance(ModelSample._parent, ReferenceProperty)
#     assert ModelSample._parent._entity == ParentModel
#     assert ModelSample.kind == part_key.kind == g_key.kind
#     assert ModelSample._parent.kind == ParentModel.kind
#     assert ModelSample._parent.project == "custom-project"
#     assert ModelSample.project == part_key.project == g_key.project == os.environ['DATASTORE_PROJECT_ID']
#     assert ModelSample._parent.namespace == "other-namespace"
#     assert ModelSample.namespace == part_key.namespace == g_key.namespace == None


def test_model_base_with_valid_properties():
    from noseiquela_orm.types.properties import (
        StringProperty, BooleanProperty,
        IntegerProperty, ListProperty,
    )

    class ModelSample(Model):
        str_prop = StringProperty()
        bool_prop = BooleanProperty()
        int_prop = IntegerProperty()
        list_prop = ListProperty()

    sample = ModelSample()
    assert sample.str_prop == sample.bool_prop == sample.int_prop == sample.list_prop == None

    sample = ModelSample(
        str_prop="str",
        bool_prop=True,
        int_prop=42,
        list_prop=[1, 2],
    )

    assert sample.str_prop == "str"
    assert sample.bool_prop is True
    assert sample.int_prop == 42
    assert sample.list_prop == [1, 2]
    assert repr(sample) == "<ModelSample - id: None>"

    sample.int_prop = 13
    sample.id = "some-id"

    assert sample.int_prop == 13
    assert repr(sample) == "<ModelSample - id: some-id>"


def test_model_base_to_dict_with_id_and_valid_properties():
    from noseiquela_orm.types.properties import (
        StringProperty, BooleanProperty,
        IntegerProperty, ListProperty,
    )

    class ModelSample(Model):
        str_prop = StringProperty()
        bool_prop = BooleanProperty()
        int_prop = IntegerProperty()
        list_prop = ListProperty()

    sample = ModelSample()
    sample.id="some-id"
    sample.str_prop = "str"
    sample.bool_prop = True
    sample.int_prop = 42
    sample.list_prop = [1, 2]

    assert sample.as_dict() == {
        "id": "some-id",
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2]
    }

    sample = ModelSample(
        id="some-id",
        str_prop="str",
        bool_prop=True,
        int_prop=42,
        list_prop=[1, 2],
    )

    assert sample.as_dict() == {
        "id": "some-id",
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2]
    }


def test_model_base_to_dict_without_id_and_with_valid_properties():
    from noseiquela_orm.types.properties import (
        StringProperty, BooleanProperty,
        IntegerProperty, ListProperty,
    )

    class ModelSample(Model):
        str_prop = StringProperty()
        bool_prop = BooleanProperty()
        int_prop = IntegerProperty()
        list_prop = ListProperty()

    sample = ModelSample()
    sample.str_prop = "str"
    sample.bool_prop = True
    sample.int_prop = 42
    sample.list_prop = [1, 2]

    assert sample.as_dict() == {
        "id": None,
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2]
    }

    sample = ModelSample(
        str_prop="str",
        bool_prop=True,
        int_prop=42,
        list_prop=[1, 2],
    )

    assert sample.as_dict() == {
        "id": None,
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2]
    }


def test_model_base_mount_from_google_entity_without_parent_key():
    from noseiquela_orm.types.properties import (
        StringProperty, BooleanProperty,
        IntegerProperty, ListProperty,
    )

    class ModelSample(Model):
        str_prop = StringProperty()
        bool_prop = BooleanProperty()
        int_prop = IntegerProperty()
        list_prop = ListProperty()

    entity_props = {
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2],
    }

    sample = ModelSample._mount_from_google_entity(mount_entity(
        kind=ModelSample.kind,
        id_or_name=1,
        **entity_props,
    ))

    assert sample.str_prop == entity_props["str_prop"]
    assert sample.bool_prop is entity_props["bool_prop"]
    assert sample.int_prop == entity_props["int_prop"]
    assert sample.list_prop == entity_props["list_prop"]
    assert sample.kind == ModelSample.kind
    assert sample.id == 1

    sample = ModelSample._mount_from_google_entity(mount_entity(
        kind="other-kind",
        id_or_name=2,
        **entity_props,
    ))

    assert sample.str_prop == entity_props["str_prop"]
    assert sample.bool_prop is entity_props["bool_prop"]
    assert sample.int_prop == entity_props["int_prop"]
    assert sample.list_prop == entity_props["list_prop"]
    assert sample.kind == ModelSample.kind
    assert sample.id == 2


# def test_model_base_mount_from_google_entity_with_parent_key():
#     from noseiquela_orm.types.key import ReferenceProperty
#     from noseiquela_orm.types.properties import (
#         StringProperty, BooleanProperty,
#         IntegerProperty, ListProperty,
#     )

#     class ParentModel(Model):
#         parent_str_prop = StringProperty()
#         parent_bool_prop = BooleanProperty()
#         parent_int_prop = IntegerProperty()
#         parent_list_prop = ListProperty()

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(ParentModel)

#         str_prop = StringProperty()
#         bool_prop = BooleanProperty()
#         int_prop = IntegerProperty()
#         list_prop = ListProperty()

#     parent_id, parent_entity_props = 13, {
#         "parent_str_prop": "other-str",
#         "parent_bool_prop": False,
#         "parent_int_prop": 13,
#         "parent_list_prop": ["a", "b"],
#     }
#     entity_id, entity_props = 42, {
#         "str_prop": "str",
#         "bool_prop": True,
#         "int_prop": 42,
#         "list_prop": [1, 2],
#     }

#     parent_entity = mount_entity(ParentModel.kind, parent_id, **parent_entity_props)
#     entity = mount_entity(ModelSample.kind, entity_id, parent_entity.key, **entity_props)

#     parent_sample = ParentModel._mount_from_google_entity(parent_entity)

#     assert parent_sample.parent_str_prop == parent_entity_props["parent_str_prop"]
#     assert parent_sample.parent_bool_prop is parent_entity_props["parent_bool_prop"]
#     assert parent_sample.parent_int_prop == parent_entity_props["parent_int_prop"]
#     assert parent_sample.parent_list_prop == parent_entity_props["parent_list_prop"]
#     assert parent_sample.kind == ParentModel.kind
#     assert parent_sample.id == 13

#     sample = ModelSample._mount_from_google_entity(entity)

#     assert sample.str_prop == entity_props["str_prop"]
#     assert sample.bool_prop is entity_props["bool_prop"]
#     assert sample.int_prop == entity_props["int_prop"]
#     assert sample.list_prop == entity_props["list_prop"]
#     assert sample.kind == ModelSample.kind
#     assert sample.id == 42
#     assert sample.parent_id == 13
#     assert ModelSample._parent._entity == ParentModel


def test_model_base_save_with_no_required_props():
    from noseiquela_orm.types.properties import (
        StringProperty, BooleanProperty,
        IntegerProperty, ListProperty,
    )

    class ModelSample(Model):
        str_prop = StringProperty()
        bool_prop = BooleanProperty()
        int_prop = IntegerProperty()
        list_prop = ListProperty()

    entity_id, entity_props = 42, {
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2],
    }

    sample = ModelSample(
        id=entity_id,
        **entity_props,
    )

    with mock.patch(
        'google.cloud.datastore.client.Batch'
    ) as batch:
        sample.save()
        batch.return_value.put.assert_called_once_with(mount_entity(
            ModelSample.kind,
            entity_id,
            **entity_props
        ))


# def test_model_base_save_with_required_props():
#     from noseiquela_orm.types.key import ReferenceProperty
#     from noseiquela_orm.types.properties import (
#         StringProperty, BooleanProperty,
#         IntegerProperty, ListProperty,
#     )

#     class ParentModel(Model):
#         parent_str_prop = StringProperty(required=True)

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(ParentModel, required=True)

#         str_prop = StringProperty(required=True)
#         bool_prop = BooleanProperty()
#         int_prop = IntegerProperty()
#         list_prop = ListProperty(required=True)

#     parent_id, parent_props = 13, {
#         "parent_str_prop": "some-str",
#     }
#     entity_id, entity_props = 42, {
#         "str_prop": "str",
#         "bool_prop": True,
#         "int_prop": 42,
#         "list_prop": [1, 2],
#     }

#     parent_entity = mount_entity(
#         ParentModel.kind,
#         parent_id,
#         **parent_props
#     )
#     parent_sample = ParentModel(id=parent_id, **parent_props)
#     entity = mount_entity(
#         ModelSample.kind,
#         entity_id,
#         parent_entity.key,
#         **entity_props
#     )
#     sample = ModelSample(
#         id=entity_id,
#         parent_id=parent_sample.id,
#         **entity_props,
#     )

#     with mock.patch(
#         'google.cloud.datastore.client.Batch'
#     ) as batch:
#         sample.save()
#         batch.return_value.put.assert_called_with(entity)
#         parent_sample.save()
#         batch.return_value.put.assert_called_with(parent_entity)
#         batch.return_value.put.call_count == 2


# def test_model_base_save_with_empty_required_props():
#     from noseiquela_orm.types.key import ReferenceProperty
#     from noseiquela_orm.types.properties import (
#         StringProperty, BooleanProperty,
#         IntegerProperty, ListProperty,
#     )

#     class ParentModel(Model):
#         parent_str_prop = StringProperty(required=True)

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(ParentModel, required=True)

#         str_prop = StringProperty(required=True)
#         bool_prop = BooleanProperty()
#         int_prop = IntegerProperty()
#         list_prop = ListProperty(required=True)

#     parent_id, parent_props = 13, {
#         "parent_str_prop": None,
#     }
#     entity_id, entity_props = 42, {
#         "str_prop": "str",
#         "bool_prop": True,
#         "int_prop": 42,
#         "list_prop": [1, 2],
#     }

#     parent_entity = mount_entity(
#         ParentModel.kind,
#         parent_id,
#         **parent_props
#     )
#     parent_sample = ParentModel(id=parent_id, **parent_props)
#     entity = mount_entity(
#         ModelSample.kind,
#         entity_id,
#         parent_entity.key,
#         **entity_props
#     )
#     sample = ModelSample(
#         id=entity_id,
#         parent_id=parent_sample.id,
#         **entity_props,
#     )

#     with mock.patch(
#         'google.cloud.datastore.client.Batch'
#     ) as batch:
#         with pytest.raises(Exception):
#             parent_sample.save()

#         sample.save()
#         batch.return_value.put.assert_called_once_with(entity)


def test_model_base_mount_entity_key_with_no_parent():
    from noseiquela_orm.types.properties import (
        StringProperty, BooleanProperty,
        IntegerProperty, ListProperty,
    )

    class ModelSample(Model):
        str_prop = StringProperty()
        bool_prop = BooleanProperty()
        int_prop = IntegerProperty()
        list_prop = ListProperty()

    entity_id, entity_props = 42, {
        "str_prop": "str",
        "bool_prop": True,
        "int_prop": 42,
        "list_prop": [1, 2],
    }

    sample = ModelSample(
        id=entity_id,
        **entity_props,
    )

    out = sample._mount_entity_g_key()

    assert out == mount_key(ModelSample.kind, entity_id)


# def test_model_base_mount_entity_key_with_parent():
#     from noseiquela_orm.types.key import ReferenceProperty
#     from noseiquela_orm.types.properties import (
#         StringProperty, BooleanProperty,
#         IntegerProperty, ListProperty,
#     )

#     class ParentModel(Model):
#         ...

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(ParentModel)

#         str_prop = StringProperty()
#         bool_prop = BooleanProperty()
#         int_prop = IntegerProperty()
#         list_prop = ListProperty()

#     parent_id = 13
#     entity_id, entity_props = 42, {
#         "str_prop": "str",
#         "bool_prop": True,
#         "int_prop": 42,
#         "list_prop": [1, 2],
#     }

#     parent_key = mount_key(ParentModel.kind, parent_id)
#     entity_key = mount_key(ModelSample.kind, entity_id, parent_key)

#     sample = ModelSample(
#         id=entity_id,
#         parent_id=parent_id,
#         **entity_props,
#     )

#     out = sample.mount_entity_key()

#     assert out == entity_key
#     assert out.id == entity_key.id == entity_id
#     assert out.kind == entity_key.kind == ModelSample.kind
#     assert out.parent.id == entity_key.parent.id
#     assert out.parent.kind == entity_key.parent.kind == ParentModel.kind


# def test_model_base_mount_entity_key_with_empty_id():
#     from noseiquela_orm.types.key import ReferenceProperty
#     from noseiquela_orm.types.properties import (
#         StringProperty, BooleanProperty,
#         IntegerProperty, ListProperty,
#     )

#     class ParentModel(Model):
#         ...

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(ParentModel)

#         str_prop = StringProperty()
#         bool_prop = BooleanProperty()
#         int_prop = IntegerProperty()
#         list_prop = ListProperty()

#     parent_id = 13
#     entity_props = {
#         "str_prop": "str",
#         "bool_prop": True,
#         "int_prop": 42,
#         "list_prop": [1, 2],
#     }

#     parent_key = mount_key(ParentModel.kind, parent_id)
#     entity_key = mount_key(ModelSample.kind, parent=parent_key)

#     sample = ModelSample(
#         parent_id=parent_id,
#         **entity_props,
#     )


#     out = sample.mount_entity_key()


    # assert out.id == entity_key.id == None
    # assert out.kind == entity_key.kind == ModelSample.kind
    # assert out.parent.id == entity_key.parent.id
    # assert out.parent.kind == entity_key.parent.kind == ParentModel.kind


# def test_model_base_mount_entity_key_with_empty_parent_id():
#     from noseiquela_orm.types.key import ReferenceProperty
#     from noseiquela_orm.types.properties import (
#         StringProperty, BooleanProperty,
#         IntegerProperty, ListProperty,
#     )

#     class ParentModel(Model):
#         ...

#     class ModelSample(Model):
#         __parent__ = ReferenceProperty(ParentModel)

#         str_prop = StringProperty()
#         bool_prop = BooleanProperty()
#         int_prop = IntegerProperty()
#         list_prop = ListProperty()

#     parent_id = 13
#     entity_props = {
#         "str_prop": "str",
#         "bool_prop": True,
#         "int_prop": 42,
#         "list_prop": [1, 2],
#     }

#     sample = ModelSample(
#         parent_id=None,
#         **entity_props,
#     )

#     with pytest.raises(Exception, match="Parent key must be complete."):
#         sample.mount_entity_key()
