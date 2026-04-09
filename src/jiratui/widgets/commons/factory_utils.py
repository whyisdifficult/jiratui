# from typing import Any
#
# from textual.widget import Widget
# from textual.widgets import Select
#
# from jiratui.widgets.commons.base import FieldMode
# from jiratui.widgets.commons.constants import CustomFieldType
# from jiratui.widgets.commons.widgets import (
#     DateInputWidget,
#     DateTimeInputWidget,
#     LabelsWidget,
#     MultiSelectWidget,
#     NumericInputWidget,
#     SelectionWidget,
#     TextInputWidget,
#     URLWidget,
# )

# TODO add missing pieces from the original PR


class AllowedValuesParser:
    """Parses the `allowedValues` field found in a Jira field's metadata dictionary into Select widget options.

    This handles the complexity of extracting display names and IDs from the various formats Jira uses for allowed
    values.
    """

    @staticmethod
    def parse_options(allowed_values: list[dict]) -> list[tuple[str, str]]:
        """Parses `allowedValues` into Select-compatible options.

        Args:
            allowed_values: list of value dictionaries from Jira metadata.

        Returns:
            List of (display_name, id) tuples for Select widget
        """

        options: list[tuple[str, str]] = []
        # Handle None or empty allowed_values
        if not allowed_values:
            return options
        for value in allowed_values:
            # Try 'name' first, fall back to 'value'
            display_value = value.get('name') or value.get('value', '')
            value_id = value.get('id', '')
            if display_value and value_id:
                options.append((display_value, value_id))
        return options
