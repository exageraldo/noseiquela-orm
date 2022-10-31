import pytest

from noseiquela_orm.utils.case_style import CaseStyle


@pytest.mark.parametrize(
    "from_case,to_case,initial_str,expected_str",
    [
        pytest.param(
            item["from_case"],
            item["to_case"],
            item["init"],
            item["exp"],
            id=f"from-{item['from_case']}-to-{item['to_case']}"
        ) for item in [
            {"from_case": "camel_case", "to_case": "camel_case", "init": "camelCase", "exp": "camelCase"},
            {"from_case": "camel_case", "to_case": "pascal_case", "init": "camelCase", "exp": "CamelCase"},
            {"from_case": "camel_case", "to_case": "kebab_case", "init": "camelCase", "exp": "camel-case"},
            {"from_case": "camel_case", "to_case": "snake_case", "init": "camelCase", "exp": "camel_case"},
            {"from_case": "pascal_case", "to_case": "camel_case", "init": "PascalCase", "exp": "pascalCase"},
            {"from_case": "pascal_case", "to_case": "pascal_case", "init": "PascalCase", "exp": "PascalCase"},
            {"from_case": "pascal_case", "to_case": "kebab_case", "init": "PascalCase", "exp": "pascal-case"},
            {"from_case": "pascal_case", "to_case": "snake_case", "init": "PascalCase", "exp": "pascal_case"},
            {"from_case": "kebab_case", "to_case": "camel_case", "init": "kebab-case", "exp": "kebabCase"},
            {"from_case": "kebab_case", "to_case": "pascal_case", "init": "kebab-case", "exp": "KebabCase"},
            {"from_case": "kebab_case", "to_case": "kebab_case", "init": "kebab-case", "exp": "kebab-case"},
            {"from_case": "kebab_case", "to_case": "snake_case", "init": "kebab-case", "exp": "kebab_case"},
            {"from_case": "snake_case", "to_case": "camel_case", "init": "snake_case", "exp": "snakeCase"},
            {"from_case": "snake_case", "to_case": "pascal_case", "init": "snake_case", "exp": "SnakeCase"},
            {"from_case": "snake_case", "to_case": "kebab_case", "init": "snake_case", "exp": "snake-case"},
            {"from_case": "snake_case", "to_case": "snake_case", "init": "snake_case", "exp": "snake_case"},
        ]
    ]
)
def test_case_style_call(
    from_case,
    to_case,
    initial_str,
    expected_str
):
    out = CaseStyle(from_case=from_case, to_case=to_case)
    assert out(initial_str) == expected_str


@pytest.mark.parametrize(
    "from_case,to_case,initial_str,expected_str",
    [
        pytest.param(
            item["from_case"],
            item["to_case"],
            item["init"],
            item["exp"],
            id=f"from-{item['from_case']}-to-{item['to_case']}"
        ) for item in [
            {"from_case": "camel_case", "to_case": "camel_case", "exp": "camelCase", "init": "camelCase"},
            {"from_case": "camel_case", "to_case": "pascal_case", "exp": "camelCase", "init": "CamelCase"},
            {"from_case": "camel_case", "to_case": "kebab_case", "exp": "camelCase", "init": "camel-case"},
            {"from_case": "camel_case", "to_case": "snake_case", "exp": "camelCase", "init": "camel_case"},
            {"from_case": "pascal_case", "to_case": "camel_case", "exp": "PascalCase", "init": "pascalCase"},
            {"from_case": "pascal_case", "to_case": "pascal_case", "exp": "PascalCase", "init": "PascalCase"},
            {"from_case": "pascal_case", "to_case": "kebab_case", "exp": "PascalCase", "init": "pascal-case"},
            {"from_case": "pascal_case", "to_case": "snake_case", "exp": "PascalCase", "init": "pascal_case"},
            {"from_case": "kebab_case", "to_case": "camel_case", "exp": "kebab-case", "init": "kebabCase"},
            {"from_case": "kebab_case", "to_case": "pascal_case", "exp": "kebab-case", "init": "KebabCase"},
            {"from_case": "kebab_case", "to_case": "kebab_case", "exp": "kebab-case", "init": "kebab-case"},
            {"from_case": "kebab_case", "to_case": "snake_case", "exp": "kebab-case", "init": "kebab_case"},
            {"from_case": "snake_case", "to_case": "camel_case", "exp": "snake_case", "init": "snakeCase"},
            {"from_case": "snake_case", "to_case": "pascal_case", "exp": "snake_case", "init": "SnakeCase"},
            {"from_case": "snake_case", "to_case": "kebab_case", "exp": "snake_case", "init": "snake-case"},
            {"from_case": "snake_case", "to_case": "snake_case", "exp": "snake_case", "init": "snake_case"},
        ]
    ]
)
def test_case_style_reverse(
    from_case,
    to_case,
    initial_str,
    expected_str
):
    out = CaseStyle(from_case=from_case, to_case=to_case)
    assert out.revert(initial_str) == expected_str
