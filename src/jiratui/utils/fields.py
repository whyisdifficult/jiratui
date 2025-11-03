"""This module provides functions for dealing with Jira fields."""

from typing import Any


def get_custom_fields_values(fields_values: dict, edit_metadata: dict) -> dict[str, Any]:
    """Retrieves the values of all the custom fields associated to an issue.

    ```{important}
    To determine if a field is a custom field we use the edit metadata associated to the work item. However, some
    (custom) fields MAY not appear in the edit metadata if they are not part of a editable screen. For example, this is
    the case with the "flagged" field. Depending on the platform's configuration this field MAY or MAY NOT appear in
    the edit metadata. As result, we also extract the value of the customs fields that appear in the issue's `fields`
    attribute. This is done by iterating over all the fields and processing the fields that start with `customfield_`.
    ```

    Args:
        fields_values: the values of all the fields known to an issue.
        edit_metadata: an issue's edit metadata's fields attribute.

    Returns:
        A dictionary with the `key` of the custom field and the (current) value of the field.
    """

    values: dict[str, Any] = {}
    for _, field_data in edit_metadata.items():
        schema = field_data.get('schema', {})
        if schema.get('customId') or schema.get('custom'):
            # the field is custom
            values[field_data.get('key')] = fields_values.get(field_data.get('key'))
    for field_key, field_value in fields_values.items():
        if not field_key.lower().startswith('customfield_'):
            continue
        # the field is custom
        if field_key not in values:
            values[field_key] = field_value
    return values


def get_field_key(name: str, edit_metadata_fields: dict) -> dict | None:
    """Retrieves the key of a Jira field from an issue's edit metadata.

    Args:
        name: the name of the field.
        edit_metadata_fields: an issue's edit metadata's fields attribute.

    Returns:
        A dictionary with the `key` of the field and the `metadata` for updating the field.
    """

    for _, field_data in edit_metadata_fields.items():
        if not (field_name := field_data.get('name')):
            continue
        if field_name.lower() != name.lower():
            continue
        return {'metadata': field_data, 'key': field_data.get('key')}
    return None
