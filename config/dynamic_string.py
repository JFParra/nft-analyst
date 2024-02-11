import re

VARIABLE_PATTERN = "\\$\\{(?P<variable>[A-Za-z0-9-_:/=.,?@!$&+ ]+)}"
QUOTED_JSON_VALUES = '("null"|"false"|"true")'
VARIABLE_PLACEHOLDER = "variable"
DEFAULT_VALUE_DELIMITER = ":"


class DynamicString:
    """
    Parse and replace dynamic placeholders within a string with values from a provided map.
    """

    @staticmethod
    def parse(source_string: str, env_vars: dict) -> str | None:
        if not source_string:
            return None

        # Don't both modifying string if no vars supplied.
        if not env_vars:
            return source_string

        no_more_dynamic_variables = False
        final_value = source_string

        while no_more_dynamic_variables is False:
            final_value = DynamicString.parse_dynamic_variables(final_value, env_vars)
            if DynamicString.contains_dynamic_values(final_value) is False:
                no_more_dynamic_variables = True

        return final_value

    @staticmethod
    def contains_dynamic_values(source_value: str) -> bool:
        result = re.search(VARIABLE_PATTERN, source_value)

        if result is not None:
            return True

        return False

    @staticmethod
    def parse_dynamic_variables(source_value: str, variable_map: dict) -> str:
        matcher = re.findall(VARIABLE_PATTERN, source_value)
        parsed_value = source_value
        if len(matcher) > 0:
            for match in matcher:
                variable_parts = DynamicString.find_variable_parts(match)

                if len(variable_parts) == 1:
                    env_var = variable_map.get(match)
                else:
                    env_var = variable_map.get(variable_parts[0])
                    if env_var is None:
                        env_var = variable_parts[1]

                if env_var is None:
                    env_var = ""

                parsed_value = parsed_value.replace("${" + match + "}", env_var)

        return parsed_value

    @staticmethod
    def find_variable_parts(variable: str) -> list[str]:
        index_of_colon = variable.find(DEFAULT_VALUE_DELIMITER)

        # If no colon was found, we can assume no default value was supplied
        if index_of_colon == -1:
            return [variable]

        variable_name = variable[0:index_of_colon]
        variable_value = variable[index_of_colon + 1 :]

        return [variable_name, variable_value]
