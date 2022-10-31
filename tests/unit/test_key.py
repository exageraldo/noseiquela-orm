import os

import pytest

from noseiquela_orm.types.key import KeyProperty

from .utils import mount_key


@pytest.fixture(scope="module")
def model_entity_with_no_parent():
    from noseiquela_orm.entity import Model

    class ModelEntity(Model):
        ...

    return ModelEntity


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None, id="None-value"),
        pytest.param(42, id="int-value"),
        pytest.param("some-str", id="str-value"),
    ]
)
def test_key_property_validate_with_valid_value(value):
    from noseiquela_orm.entity import Model

    class ModelSample(Model):
        id = KeyProperty()

    model_obj = ModelSample(id=value)

    assert model_obj.id == value

    other_obj = ModelSample()
    other_obj.id = value

    assert other_obj.id == value

@pytest.mark.parametrize(
    "value",
    [
        pytest.param(10.0, id="float-value"),
        pytest.param({}, id="empty-dict-value"),
        pytest.param([123], id="list-of-int-value"),
        pytest.param(["str"], id="list-of-str-value"),
    ]
)
def test_key_property_validate_with_invalid_value(value):
    from noseiquela_orm.entity import Model

    class ModelSample(Model):
        id = KeyProperty()

    with pytest.raises(ValueError):
        ModelSample(id=value)

    model_obj = ModelSample()
    with pytest.raises(ValueError):
        model_obj.id = value



def test_mount_partial_key_property_with_no_parent():
    from noseiquela_orm.entity import Model

    class ModelSample(Model):
        id = KeyProperty()

    assert hasattr(ModelSample, "_partial_g_key")
    assert hasattr(ModelSample, "_complete_g_key")
    assert not hasattr(ModelSample, "parent_id")
    assert not hasattr(ModelSample, "_parent_complete_g_key")

    exp_key = mount_key(ModelSample.kind)
    out = ModelSample._partial_g_key()

    assert out.kind == exp_key.kind == ModelSample.kind
    assert out.id == exp_key.id == None
    assert out.project == exp_key.project == os.environ['DATASTORE_PROJECT_ID']
    assert out.namespace == exp_key.namespace == None


def test_mount_partial_key_property_with_complete_parent():
    from noseiquela_orm.entity import Model

    class ParentSample(Model):
        ...

    class ModelSample(Model):
        id = KeyProperty(parent=ParentSample)

    assert hasattr(ModelSample, "_partial_g_key")
    assert hasattr(ModelSample, "_complete_g_key")
    assert hasattr(ModelSample, "parent_id")
    assert hasattr(ModelSample, "_parent_complete_g_key")
    assert hasattr(ParentSample, "_partial_g_key")
    assert hasattr(ParentSample, "_complete_g_key")
    assert not hasattr(ParentSample, "parent_id")
    assert not hasattr(ParentSample, "_parent_complete_g_key")

    parent_id = 42

    parent_key = mount_key(ParentSample.kind, parent_id)
    exp_key = mount_key(ModelSample.kind, parent=parent_key)

    out = ModelSample._partial_g_key(
        parent=ModelSample._parent_complete_g_key(id_or_name=parent_id)
    )

    assert out.id == exp_key.id == None
    assert out.kind == exp_key.kind == ModelSample.kind
    assert out.parent.id == exp_key.parent.id == parent_key.id == parent_id
    assert out.parent.kind == exp_key.parent.kind == parent_key.kind == ParentSample.kind


def test_mount_partial_key_property_with_incomplete_parent():
    from noseiquela_orm.entity import Model

    class ParentSample(Model):
        ...

    class ModelSample(Model):
        id = KeyProperty(parent=ParentSample)

    assert hasattr(ModelSample, "_partial_g_key")
    assert hasattr(ModelSample, "_complete_g_key")
    assert hasattr(ModelSample, "parent_id")
    assert hasattr(ModelSample, "_parent_complete_g_key")
    assert hasattr(ParentSample, "_partial_g_key")
    assert hasattr(ParentSample, "_complete_g_key")
    assert not hasattr(ParentSample, "parent_id")
    assert not hasattr(ParentSample, "_parent_complete_g_key")

    parent_id = 42

    parent_key = mount_key(ParentSample.kind, parent_id)
    exp_key = mount_key(ModelSample.kind, parent=parent_key)

    with pytest.raises(Exception):
        ModelSample._partial_g_key(
            parent=ModelSample._partial_g_key()
        )


@pytest.mark.parametrize(
    "key_id",
    [
        pytest.param(42, id="int-key"),
        pytest.param("some-str", id="str-key"),
    ]
)
def test_mount_complete_key_property_with_no_parent(
    key_id,
):
    from noseiquela_orm.entity import Model

    class ModelSample(Model):
        id = KeyProperty()

    exp_key = mount_key(ModelSample.kind, key_id)

    out = ModelSample._complete_g_key(
        id_or_name=key_id
    )

    assert out.id_or_name == exp_key.id_or_name == key_id
    assert out.kind == exp_key.kind == ModelSample.kind


@pytest.mark.parametrize(
    "parent_key_id",
    [
        pytest.param(13, id="int-parent-key"),
        pytest.param("other-str", id="str-parent-key"),
    ]
)
@pytest.mark.parametrize(
    "key_id",
    [
        pytest.param(42, id="int-key"),
        pytest.param("some-str", id="str-key"),
    ]
)
def test_mount_complete_key_property_with_complete_parent(
    key_id,
    parent_key_id,
):
    from noseiquela_orm.entity import Model

    class ParentSample(Model):
        ...

    class ModelSample(Model):
        id = KeyProperty(parent=ParentSample)

    parent_key = mount_key(ParentSample.kind, parent_key_id)
    exp_key = mount_key(ModelSample.kind, key_id, parent_key)

    out = ModelSample._complete_g_key(
        id_or_name=key_id,
        parent=ModelSample._parent_complete_g_key(id_or_name=parent_key_id)
    )

    assert out.id_or_name == exp_key.id_or_name == key_id
    assert out.kind == exp_key.kind == ModelSample.kind
    assert out.parent.id_or_name == exp_key.parent.id_or_name == parent_key.id_or_name == parent_key_id
    assert out.parent.kind == exp_key.parent.kind == parent_key.kind == ParentSample.kind


@pytest.mark.parametrize(
    "key_id",
    [
        pytest.param(42, id="int-key"),
        pytest.param("some-str", id="str-key"),
    ]
)
def test_mount_complete_key_property_with_incomplete_parent(
    key_id,
):
    from noseiquela_orm.entity import Model

    class ParentSample(Model):
        ...

    class ModelSample(Model):
        id = KeyProperty(parent=ParentSample)

    with pytest.raises(Exception):
        ModelSample._complete_g_key(
            id_or_name=key_id,
            parent=ModelSample._partial_g_key()
        )
