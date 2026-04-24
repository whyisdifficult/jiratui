from unittest.mock import Mock

import pytest
from textual.widgets import Select

from jiratui.widgets.commons import FieldMode
from jiratui.widgets.commons.factory_utils import FieldMetadata, WidgetBuilder
from jiratui.widgets.commons.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    LabelsWidget,
    MultiSelectWidget,
    NumericInputWidget,
    SelectionWidget,
    SingleUserPickerWidget,
    TextInputWidget,
    URLWidget,
)


@pytest.fixture
def metadata():
    return {
        'fieldId': 'field_a',
        'name': 'Field A',
        'key': 'field_a',
        'required': True,
        'schema': {},
        'custom': None,
        'type': '',
        'allowedValues': [],
        'hasDefaultValue': False,
        'defaultValue': '',
        'operations': ['set'],
    }


@pytest.fixture
def field_metadata(metadata) -> FieldMetadata:
    return FieldMetadata(metadata)


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        ({}, None),
        ({'accountId': '1', 'displayName': 'Bart'}, {'account_id': '1', 'name': 'Bart'}),
        ({'accountId': '1', 'name': 'Bart'}, {'account_id': '1', 'name': 'Bart'}),
    ],
)
@pytest.mark.asyncio
async def test_build_user_picker_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_user_picker(
            FieldMode.UPDATE, FieldMetadata(metadata), current_value
        )
    # THEN
    assert isinstance(widget, SingleUserPickerWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value


@pytest.mark.asyncio
async def test_build_user_picker_update_mode_raises_value_error(metadata, app):
    async with app.run_test():
        # WHEN
        with pytest.raises(
            ValueError, match='Missing required accountId and/or displayName or name'
        ):
            WidgetBuilder.build_user_picker(
                FieldMode.UPDATE, FieldMetadata(metadata), {'account_id': '1', 'name': 'Bart'}
            )


@pytest.mark.asyncio
async def test_build_user_picker_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_user_picker(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, SingleUserPickerWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, None),
        (1.2, 1.2),
    ],
)
@pytest.mark.asyncio
async def test_build_numeric_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_numeric(
            FieldMode.UPDATE, FieldMetadata(metadata), current_value
        )
    # THEN
    assert isinstance(widget, NumericInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value


@pytest.mark.asyncio
async def test_build_numeric_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_numeric(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, NumericInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, None),
        ('2026-01-01', '2026-01-01'),
    ],
)
@pytest.mark.asyncio
async def test_build_date_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_date(FieldMode.UPDATE, FieldMetadata(metadata), current_value)
    # THEN
    assert isinstance(widget, DateInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value
    assert widget.valid_empty is False


@pytest.mark.asyncio
async def test_build_date_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_date(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, DateInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.valid_empty is False


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, None),
        ('2026-01-01 13:45', '2026-01-01 13:45'),
        ('', ''),
        (' ', ' '),
    ],
)
@pytest.mark.asyncio
async def test_build_datetime_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_datetime(
            FieldMode.UPDATE, FieldMetadata(metadata), current_value
        )
    # THEN
    assert isinstance(widget, DateTimeInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value
    assert widget.valid_empty is False


@pytest.mark.asyncio
async def test_build_datetime_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_datetime(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, DateTimeInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.valid_empty is False


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, ''),
        ('hello world', 'hello world'),
        ('hello world ', 'hello world '),
        ('', ''),
    ],
)
@pytest.mark.asyncio
async def test_build_text_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_text(FieldMode.UPDATE, FieldMetadata(metadata), current_value)
    # THEN
    assert isinstance(widget, TextInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value
    assert widget.valid_empty is False


@pytest.mark.asyncio
async def test_build_text_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_text(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, TextInputWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.valid_empty is False


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, ''),
        ('hello world', 'hello world'),
        ('hello world ', 'hello world '),
        ('', ''),
    ],
)
@pytest.mark.asyncio
async def test_build_url_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_url(FieldMode.UPDATE, FieldMetadata(metadata), current_value)
    # THEN
    assert isinstance(widget, URLWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value
    assert widget.valid_empty is False


@pytest.mark.asyncio
async def test_build_url_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_url(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, URLWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.valid_empty is False


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, []),
        ([], []),
        (['test1', 'test2'], ['test1', 'test2']),
    ],
)
@pytest.mark.asyncio
async def test_build_labels_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_labels(
            FieldMode.UPDATE, FieldMetadata(metadata), current_value
        )
    # THEN
    assert isinstance(widget, LabelsWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value
    assert widget.valid_empty is False


@pytest.mark.asyncio
async def test_build_labels_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_labels(FieldMode.CREATE, FieldMetadata(metadata), None)
    # THEN
    assert isinstance(widget, LabelsWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.valid_empty is False


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, []),
        ([], []),
        (['test1', 'test2'], []),
        ([{'id': '1'}], ['1']),
        ([Mock(id='2')], ['2']),
    ],
)
@pytest.mark.asyncio
async def test_build_multicheckboxes_update_mode(
    current_value, expected_original_value, metadata, app
):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_multicheckboxes(
            FieldMode.UPDATE, FieldMetadata(metadata), current_value
        )
    # THEN
    assert isinstance(widget, MultiSelectWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value


@pytest.mark.asyncio
async def test_build_multicheckboxes_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_multicheckboxes(
            FieldMode.CREATE, FieldMetadata(metadata), None
        )
    # THEN
    assert isinstance(widget, MultiSelectWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE


@pytest.mark.parametrize(
    'current_value, expected_original_value',
    [
        (None, None),
        ('', None),
        ('test1', 'test1'),
        ({'id': 'test1'}, 'test1'),
    ],
)
@pytest.mark.asyncio
async def test_build_selection_update_mode(current_value, expected_original_value, metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_selection(
            FieldMode.UPDATE,
            FieldMetadata(metadata),
            options=[('', Select.NULL), ('Test A', 'test1')],
            current_value=current_value,
        )
    # THEN
    assert isinstance(widget, SelectionWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.UPDATE
    assert widget.original_value == expected_original_value
    assert widget.selection == expected_original_value


@pytest.mark.asyncio
async def test_build_build_selection_create_mode(metadata, app):
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_selection(
            FieldMode.CREATE,
            FieldMetadata(metadata),
            options=[('', Select.NULL)],
            current_value=None,
        )
    # THEN
    assert isinstance(widget, SelectionWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.selection is None


@pytest.mark.asyncio
async def test_build_build_selection_create_mode_with_default_value(metadata, app):
    # GIVEN
    metadata['hasDefaultValue'] = True
    metadata['defaultValue'] = {'id': 'test1'}
    async with app.run_test():
        # WHEN
        widget = WidgetBuilder.build_selection(
            FieldMode.CREATE,
            FieldMetadata(metadata),
            options=[('', Select.NULL), ('Test A', 'test1')],
            current_value=None,
        )
    # THEN
    assert isinstance(widget, SelectionWidget)
    assert widget.field_id == 'field_a'
    assert widget.jira_field_key == 'field_a'
    assert widget.mode == FieldMode.CREATE
    assert widget.selection == 'test1'
