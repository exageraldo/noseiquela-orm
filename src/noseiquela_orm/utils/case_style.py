from typing import TYPE_CHECKING
from re import finditer

if TYPE_CHECKING:
    from typing import List


class CaseStyle:
    def __init__(self, from_case: 'str'="snake_case", to_case: 'str'="camel_case") -> 'None':
        self.from_case = from_case
        self.to_case = to_case

    @staticmethod
    def _from_case_style(case_style: 'str', string_value: 'List[str]') -> 'str':
        parse_functions = {
            "camel_case": lambda string_value: [
                w.group(0) for w in finditer(
                    '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',
                    string_value
                )
            ],
            "pascal_case": lambda string_value: [
                w.group(0) for w in finditer(
                    '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',
                    string_value
                )
            ],
            "pascal_case": lambda string_value: string_value.split('-'),
            "snake_case": lambda string_value: string_value.split('_')
        }

        return parse_functions[case_style](string_value)


    @staticmethod
    def _to_case_style(case_style: 'str', key_list: 'List[str]') -> 'str':
        parse_functions = {
            "camel_case": lambda key_list: key_list[0].lower() + ''.join(
                [x.title() for x in key_list[1:]]
            ),
            "pascal_case": lambda key_list: ''.join(
                [x.title() for x in key_list]
            ),
            "pascal_case": lambda key_list: '-'.join(
                [x.lower() for x in key_list]
            ),
            "snake_case": lambda key_list: '_'.join(
                [x.lower() for x in key_list]
            )
        }

        return parse_functions[case_style](key_list)

    def revert(self, value: 'str') -> 'str':
        if self.from_case == self.to_case:
            return value

        splitad_value = self._from_case_style(self.to_case, value)
        return self._to_case_style(self.from_case, splitad_value)

    def __call__(self, value: 'str') -> 'str':
        if self.from_case == self.to_case:
            return value

        splitad_value = self._from_case_style(self.from_case, value)
        return self._to_case_style(self.to_case, splitad_value)
