"""This module provides functions for dealing with Jira fields."""

from typing import Any


def get_custom_fields_values(fields_values: dict, edit_metadata: dict) -> dict[str, Any]:
    """Retrieves the values of all the custom fields associated to an issue.

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
            # the field is a custom field
            values[field_data.get('key')] = fields_values.get(field_data.get('key'))
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
