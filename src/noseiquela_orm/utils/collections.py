from typing import Dict, TypeVar

_Keys = TypeVar("_Keys")
_Values = TypeVar("_Values")


def merge_dicts(
    left: Dict[_Keys, _Values],
    right: Dict[_Keys, _Values],
    /,
) -> Dict[_Keys, _Values]:
    """Merge two dictionaries together into a new dict with keys from both dicts.

    Note that the values from the right dict will overwrite the values from the left one
    if the same key is present in both dicts:

    ```python
    >>> left = {"a": 1, "b": 2}
    >>> right = {"b": 3, "c": 4}
    >>> merge_dicts(left, right)
    {"a": 1, "b": 3, "c": 4}
    ```

    This function backports the dictionary union operator from python3.9 to python3.8.
    """

    # TODO(python3.9): replace this function with the dictionary union operator when
    # support for python3.8 is dropped
    return {**left, **right}
