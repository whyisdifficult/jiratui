import pytest

from jiratui.utils.fields import get_custom_fields_values, get_field_key


@pytest.fixture()
def edit_metadata() -> dict:
    return {
        'summary': {
            'required': True,
            'schema': {'type': 'string', 'system': 'summary'},
            'name': 'Summary',
            'key': 'summary',
            'operations': ['set'],
        },
        'customfield_10021': {
            'required': False,
            'schema': {
                'type': 'array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10021,
            },
            'name': 'Flagged',
            'key': 'customfield_10021',
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
        },
        'customfield_10022': {
            'required': False,
            'schema': {
                'type': 'array',
                'items': 'option',
                'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                'customId': 10022,
            },
            'key': 'customfield_10022',
            'operations': ['add', 'set', 'remove'],
            'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
        },
    }


@pytest.fixture()
def fields_values() -> dict:
    return {
        'customfield_10021': [{'value': 'Impediment', 'id': '10019'}],
        'summary': 'Add support for flagging work items',
    }


@pytest.mark.parametrize(
    'name, expected_result',
    [
        ('field_1', None),
        (
            'summary',
            {
                'metadata': {
                    'required': True,
                    'schema': {'type': 'string', 'system': 'summary'},
                    'name': 'Summary',
                    'key': 'summary',
                    'operations': ['set'],
                },
                'key': 'summary',
            },
        ),
        (
            'SummarY',
            {
                'metadata': {
                    'required': True,
                    'schema': {'type': 'string', 'system': 'summary'},
                    'name': 'Summary',
                    'key': 'summary',
                    'operations': ['set'],
                },
                'key': 'summary',
            },
        ),
        (
            'Flagged',
            {
                'metadata': {
                    'required': False,
                    'schema': {
                        'type': 'array',
                        'items': 'option',
                        'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes',
                        'customId': 10021,
                    },
                    'name': 'Flagged',
                    'key': 'customfield_10021',
                    'operations': ['add', 'set', 'remove'],
                    'allowedValues': [{'value': 'Impediment', 'id': '10019'}],
                },
                'key': 'customfield_10021',
            },
        ),
    ],
)
def test_get_field_key(edit_metadata: dict, name: str, expected_result: dict | None):
    result = get_field_key(name, edit_metadata)
    assert result == expected_result


def test_get_custom_fields_values(edit_metadata: dict, fields_values: dict):
    result = get_custom_fields_values(fields_values, edit_metadata)
    assert result == {
        'customfield_10021': [{'value': 'Impediment', 'id': '10019'}],
        'customfield_10022': None,
    }
