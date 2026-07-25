import pytest

from jiratui.widgets.commons.factory_utils import (
    AllowedValuesParser,
    FieldMetadata,
    FieldMode,
    WidgetBuilder,
)


@pytest.mark.parametrize(
    'allowed_values,expected',
    [
        ([{'id': '10001', 'name': 'Bug'}], [('Bug', '10001')]),
        ([{'id': '3', 'value': 'High'}], [('High', '3')]),
        ([{'languageCode': 'en', 'displayName': 'English'}], [('English', 'en')]),
    ],
)
def test_parse_options_supports_alternative_shapes(allowed_values, expected):
    assert AllowedValuesParser.parse_options(allowed_values) == expected


def test_build_selection_for_service_desk_language_field():
    """A `sd-request-lang` field must not crash the details worker. See issue #311."""

    allowed_values = [{'languageCode': 'en', 'displayName': 'English'}]
    metadata = FieldMetadata(
        {
            'fieldId': 'customfield_10053',
            'key': 'customfield_10053',
            'name': 'Request language',
            'schema': {'type': 'sd-request-lang'},
            'operations': [],
        }
    )

    widget = WidgetBuilder.build_selection(
        mode=FieldMode.UPDATE,
        metadata=metadata,
        options=AllowedValuesParser.parse_options(allowed_values),
        current_value='en',
    )

    assert widget.value == 'en'
