import pytest
from textual.widgets import Select

from jiratui.widgets.work_item_details.fields import (
    WorkItemDynamicFieldUpdateDateWidget,
    WorkItemDynamicFieldUpdateNumericWidget,
    WorkItemDynamicFieldUpdateSelectionWidget,
    WorkItemDynamicFieldUpdateTextWidget,
    WorkItemDynamicFieldUpdateWidget,
)


@pytest.mark.parametrize(
    'original_value, value, has_changed',
    [
        ('', '', False),
        ('', ' ', False),
        ('', 'some value', True),
        (' ', '', False),
        (' ', ' ', False),
        (' ', 'some value', True),
        ('some value', '', True),
        ('some value ', '', True),
        ('some value', ' ', True),
        ('some value', 'some value', False),
        ('some other value', 'some value', True),
    ],
)
@pytest.mark.asyncio
async def test_text_widget_values(app, original_value, value, has_changed):
    async with app.run_test():
        widget = WorkItemDynamicFieldUpdateTextWidget(
            field_supports_update=True,
            original_value=original_value,
            value=value,
        )
        assert widget.value_has_changed is has_changed


@pytest.mark.parametrize(
    'original_value, value, has_changed',
    [
        ('', '', False),
        ('', ' ', False),
        ('', '1', True),
        (' ', '', False),
        (' ', ' ', False),
        (' ', '1', True),
        ('1', '', True),
        ('1', ' ', True),
        ('1', '1', False),
        ('0', '1', True),
    ],
)
@pytest.mark.asyncio
async def test_numeric_widget_values(app, original_value, value, has_changed):
    async with app.run_test():
        widget = WorkItemDynamicFieldUpdateNumericWidget(
            field_supports_update=True,
            original_value=original_value,
            value=value,
        )
        assert widget.value_has_changed is has_changed


@pytest.mark.parametrize(
    'original_value, value, has_changed',
    [
        ('', '', False),
        ('', ' ', False),
        ('', '1', True),
        (' ', '', False),
        (' ', ' ', False),
        (' ', '1', True),
        ('1', '', True),
        ('1', ' ', True),
        ('1', '1', False),
        ('0', '1', True),
    ],
)
@pytest.mark.asyncio
async def test_generic_widget_values(app, original_value, value, has_changed):
    async with app.run_test():
        widget = WorkItemDynamicFieldUpdateWidget(
            field_supports_update=True,
            original_value=original_value,
            value=value,
        )
        assert widget.value_has_changed is has_changed


@pytest.mark.parametrize(
    'original_value, value, has_changed',
    [
        ('', '', False),
        ('', ' ', False),
        ('', '2025-12-31', True),
        (' ', '', False),
        (' ', ' ', False),
        (' ', '2025-12-31', True),
        ('2025-12-31', '', True),
        ('2025-12-31', ' ', True),
        ('2025-12-31', '2025-12-31', False),
        ('2025-12-30', '2025-12-31', True),
    ],
)
@pytest.mark.asyncio
async def test_date_widget_values(app, original_value, value, has_changed):
    async with app.run_test():
        widget = WorkItemDynamicFieldUpdateDateWidget(
            field_supports_update=True,
            original_value=original_value,
            value=value,
        )
        assert widget.value_has_changed is has_changed


@pytest.mark.parametrize(
    'original_value, value, has_changed',
    [
        (None, Select.BLANK, False),
        (None, '0', True),
        ('0', Select.BLANK, True),
        ('0', '0', False),
    ],
)
@pytest.mark.asyncio
async def test_single_selection_widget_values(app, original_value, value, has_changed):
    async with app.run_test():
        widget = WorkItemDynamicFieldUpdateSelectionWidget(
            options=[('0', '0'), ('1', '1')],
            field_supports_update=True,
            original_value=original_value,
            value=original_value,
            allow_blank=True,
        )
        widget.value = value
        assert widget.value_has_changed is has_changed
