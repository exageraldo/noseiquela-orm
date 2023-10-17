import pytest

from noseiquela_orm.utils.collections import merge_dicts


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ({}, {}, {}),
        ({"a": 1}, {}, {"a": 1}),
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": 1, "b": 2}, {"b": 3, "c": 4}, {"a": 1, "b": 3, "c": 4}),
    ],
)
def test_merge_dicts(left, right, expected):
    assert merge_dicts(left, right) == expected
