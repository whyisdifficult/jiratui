"""
Tests for unified widgets module.

Tests both CREATE and UPDATE modes for all widget types:
- DateInputWidget
- DateTimeInputWidget
- TextInputWidget
- NumericInputWidget
- SelectionWidget
"""

import pytest
from textual.widgets import Input, MaskedInput, Select

from jiratui.widgets.common.base_fields import FieldMode
from jiratui.widgets.common.widgets import (
    DateInputWidget,
    DateTimeInputWidget,
    NumericInputWidget,
    SelectionWidget,
    TextInputWidget,
)

# ============================================================================
# Date Widget Tests
# ============================================================================


class TestDateInputWidget:
    """Tests for DateInputWidget in both CREATE and UPDATE modes."""

    def test_create_mode_initialization(self):
        """Test DateInputWidget initialization in CREATE mode."""
        widget = DateInputWidget(
            mode=FieldMode.CREATE,
            field_id='duedate',
            title='Due Date',
            required=False,
        )

        assert widget.mode == FieldMode.CREATE
        assert widget.field_id == 'duedate'
        assert widget.border_title == 'Due Date'
        assert widget.compact is False
        assert 'input-date' in widget.classes

    def test_create_mode_required_field(self):
        """Test DateInputWidget with required flag in CREATE mode."""
        widget = DateInputWidget(
            mode=FieldMode.CREATE,
            field_id='duedate',
            title='Due Date',
            required=True,
        )

        assert widget.border_subtitle == '(*)'
        assert 'required' in widget.classes
        assert widget.valid_empty is False

    @pytest.mark.asyncio
    async def test_update_mode_initialization(self, app):
        """Test DateInputWidget initialization in UPDATE mode."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                title='Due Date',
                original_value='2025-12-23',
                field_supports_update=True,
            )

            assert widget.mode == FieldMode.UPDATE
            assert widget.field_id == 'duedate'
            assert widget.jira_field_key == 'duedate'
            assert widget.original_value == '2025-12-23'
            assert widget.value == '2025-12-23'
            assert widget.disabled is False

    @pytest.mark.asyncio
    async def test_update_mode_disabled_field(self, app):
        """Test DateInputWidget with update disabled."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
                field_supports_update=False,
            )

            assert widget.disabled is True

    @pytest.mark.asyncio
    async def test_get_value_for_update_valid_date(self, app):
        """Test get_value_for_update with valid date."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
            )

            widget.value = '2025-12-25'
            result = widget.get_value_for_update()
            assert result == '2025-12-25'

    @pytest.mark.asyncio
    async def test_get_value_for_update_empty(self, app):
        """Test get_value_for_update with empty value."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
            )

            widget.value = ''
            result = widget.get_value_for_update()
            assert result is None

    @pytest.mark.asyncio
    async def test_get_value_for_update_invalid_date(self, app):
        """Test get_value_for_update with invalid date format."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
            )

            # MaskedInput validates the value format, so invalid dates raise ValueError
            with pytest.raises(ValueError, match='does not match template'):
                widget.value = 'invalid-date'

    def test_get_value_for_update_in_create_mode_raises(self):
        """Test that get_value_for_update raises error in CREATE mode."""
        widget = DateInputWidget(
            mode=FieldMode.CREATE,
            field_id='duedate',
        )

        with pytest.raises(ValueError, match='only valid in UPDATE mode'):
            widget.get_value_for_update()

    @pytest.mark.asyncio
    async def test_value_has_changed_no_change(self, app):
        """Test value_has_changed when value hasn't changed."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
            )

            widget.value = '2025-12-23'
            assert widget.value_has_changed is False

    @pytest.mark.asyncio
    async def test_value_has_changed_modified(self, app):
        """Test value_has_changed when value is modified."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
            )

            widget.value = '2025-12-25'
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_empty_to_value(self, app):
        """Test value_has_changed from empty to value."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value=None,
            )

            widget.value = '2025-12-25'
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_value_to_empty(self, app):
        """Test value_has_changed from value to empty."""
        async with app.run_test():
            widget = DateInputWidget(
                mode=FieldMode.UPDATE,
                field_id='duedate',
                original_value='2025-12-23',
            )

            widget.value = ''
            assert widget.value_has_changed is True

    def test_value_has_changed_both_empty(self):
        """Test value_has_changed when both are empty."""
        widget = DateInputWidget(
            mode=FieldMode.UPDATE,
            field_id='duedate',
            original_value=None,
        )

        widget.value = ''
        assert widget.value_has_changed is False

    def test_value_has_changed_in_create_mode_raises(self):
        """Test that value_has_changed raises error in CREATE mode."""
        widget = DateInputWidget(
            mode=FieldMode.CREATE,
            field_id='duedate',
        )

        with pytest.raises(ValueError, match='only valid in UPDATE mode'):
            _ = widget.value_has_changed


# ============================================================================
# DateTime Widget Tests
# ============================================================================


class TestDateTimeInputWidget:
    """Tests for DateTimeInputWidget in both CREATE and UPDATE modes."""

    def test_create_mode_initialization(self):
        """Test DateTimeInputWidget initialization in CREATE mode."""
        widget = DateTimeInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10001',
            title='Event Time',
            required=False,
        )

        assert widget.mode == FieldMode.CREATE
        assert widget.field_id == 'customfield_10001'
        assert widget.border_title == 'Event Time'
        assert 'create-work-item-datetime-input' in widget.classes

    @pytest.mark.asyncio
    async def test_update_mode_initialization(self, app):
        """Test DateTimeInputWidget initialization in UPDATE mode."""
        async with app.run_test():
            widget = DateTimeInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                title='Event Time',
                original_value='2025-12-23 13:45:10',
                field_supports_update=True,
            )

            assert widget.mode == FieldMode.UPDATE
            assert widget.jira_field_key == 'customfield_10001'
            assert widget.original_value == '2025-12-23 13:45:10'
            assert widget.value == '2025-12-23 13:45:10'
            assert 'issue_details_input_field' in widget.classes

    @pytest.mark.asyncio
    async def test_get_value_for_update_valid_datetime(self, app):
        """Test get_value_for_update with valid datetime."""
        async with app.run_test():
            widget = DateTimeInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value='2025-12-23 13:45:10',
            )

            widget.value = '2025-12-23 14:30:00'
            result = widget.get_value_for_update()
            # Should return ISO format
            assert result is not None
            assert '2025-12-23' in result
            assert '14:30:00' in result

    @pytest.mark.asyncio
    async def test_get_value_for_update_empty(self, app):
        """Test get_value_for_update with empty value."""
        async with app.run_test():
            widget = DateTimeInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value='2025-12-23 13:45:10',
            )

            widget.value = ''
            result = widget.get_value_for_update()
            assert result is None

    @pytest.mark.asyncio
    async def test_value_has_changed_modified(self, app):
        """Test value_has_changed when datetime is modified."""
        async with app.run_test():
            widget = DateTimeInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value='2025-12-23 13:45:10',
            )

            widget.value = '2025-12-23 14:30:00'
            assert widget.value_has_changed is True


# ============================================================================
# Text Widget Tests
# ============================================================================


class TestTextInputWidget:
    """Tests for TextInputWidget in both CREATE and UPDATE modes."""

    def test_create_mode_initialization(self):
        """Test TextInputWidget initialization in CREATE mode."""
        widget = TextInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            title='Custom Text',
            required=True,
        )

        assert widget.mode == FieldMode.CREATE
        assert widget.field_id == 'customfield_10002'
        assert widget.border_title == 'Custom Text'
        assert widget.border_subtitle == '(*)'
        assert 'required' in widget.classes
        assert 'create-work-item-generic-input-field' in widget.classes

    def test_create_mode_with_placeholder(self):
        """Test TextInputWidget with custom placeholder."""
        widget = TextInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            placeholder='Enter custom text...',
        )

        assert widget.placeholder == 'Enter custom text...'

    @pytest.mark.asyncio
    async def test_update_mode_initialization(self, app):
        """Test TextInputWidget initialization in UPDATE mode."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                title='Custom Text',
                original_value='original text',
                field_supports_update=True,
            )

            assert widget.mode == FieldMode.UPDATE
            assert widget.jira_field_key == 'customfield_10002'
            assert widget.original_value == 'original text'
            assert widget.value == 'original text'
            assert 'issue_details_input_field' in widget.classes

    @pytest.mark.asyncio
    async def test_get_value_for_update(self, app):
        """Test get_value_for_update returns current value."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='original',
            )

            widget.value = 'updated text'
            result = widget.get_value_for_update()
            assert result == 'updated text'

    @pytest.mark.asyncio
    async def test_value_has_changed_no_change(self, app):
        """Test value_has_changed when value hasn't changed."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='original text',
            )

            widget.value = 'original text'
            assert widget.value_has_changed is False

    @pytest.mark.asyncio
    async def test_value_has_changed_with_whitespace(self, app):
        """Test value_has_changed ignores whitespace differences."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='original text',
            )

            widget.value = ' original text '
            # Should not detect change due to whitespace stripping
            assert widget.value_has_changed is False

    @pytest.mark.asyncio
    async def test_value_has_changed_modified(self, app):
        """Test value_has_changed when value is modified."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='original text',
            )

            widget.value = 'updated text'
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_empty_to_empty(self, app):
        """Test value_has_changed when both are empty."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='',
            )

            widget.value = '   '  # Whitespace only
            assert widget.value_has_changed is False

    @pytest.mark.asyncio
    async def test_value_has_changed_empty_to_value(self, app):
        """Test value_has_changed from empty to value."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='',
            )

            widget.value = 'new text'
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_value_to_empty(self, app):
        """Test value_has_changed from value to empty."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value='original text',
            )

            widget.value = ''
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_none_to_value(self, app):
        """Test value_has_changed from None to value."""
        async with app.run_test():
            widget = TextInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10002',
                original_value=None,
            )

            widget.value = 'new text'
            assert widget.value_has_changed is True


# ============================================================================
# Numeric Widget Tests
# ============================================================================


class TestNumericInputWidget:
    """Tests for NumericInputWidget in both CREATE and UPDATE modes."""

    def test_create_mode_initialization(self):
        """Test NumericInputWidget initialization in CREATE mode."""
        widget = NumericInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10001',
            title='Story Points',
            required=False,
        )

        assert widget.mode == FieldMode.CREATE
        assert widget.field_id == 'customfield_10001'
        assert widget.border_title == 'Story Points'
        assert widget.compact is False
        assert 'create-work-item-float-input' in widget.classes

    def test_create_mode_required_field(self):
        """Test NumericInputWidget with required flag in CREATE mode."""
        widget = NumericInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10001',
            title='Story Points',
            required=True,
        )

        assert widget.border_subtitle == '(*)'
        assert 'required' in widget.classes

    @pytest.mark.asyncio
    async def test_update_mode_initialization(self, app):
        """Test NumericInputWidget initialization in UPDATE mode."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                title='Story Points',
                original_value=5.0,
                field_supports_update=True,
            )

            assert widget.mode == FieldMode.UPDATE
            assert widget.field_id == 'customfield_10001'
            assert widget.jira_field_key == 'customfield_10001'
            assert widget.original_value == 5.0
            assert widget.value == '5.0'
            assert widget.disabled is False
            assert 'issue_details_input_field' in widget.classes

    @pytest.mark.asyncio
    async def test_update_mode_disabled_field(self, app):
        """Test NumericInputWidget with update disabled."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
                field_supports_update=False,
            )

            assert widget.disabled is True

    def test_update_mode_none_original_value(self):
        """Test NumericInputWidget with None original value."""
        widget = NumericInputWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10001',
            original_value=None,
        )

        assert widget.original_value is None
        assert widget.value == ''

    @pytest.mark.asyncio
    async def test_get_value_for_update_valid_float(self, app):
        """Test get_value_for_update with valid float."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = '7.5'
            result = widget.get_value_for_update()
            assert result == 7.5

    @pytest.mark.asyncio
    async def test_get_value_for_update_integer(self, app):
        """Test get_value_for_update with integer value."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = '10'
            result = widget.get_value_for_update()
            assert result == 10.0

    @pytest.mark.asyncio
    async def test_get_value_for_update_empty(self, app):
        """Test get_value_for_update with empty value."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = ''
            result = widget.get_value_for_update()
            assert result is None

    @pytest.mark.asyncio
    async def test_get_value_for_update_invalid(self, app):
        """Test get_value_for_update with invalid value."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = 'not-a-number'
            result = widget.get_value_for_update()
            assert result is None

    def test_get_value_for_update_wrong_mode(self):
        """Test get_value_for_update raises error in CREATE mode."""
        widget = NumericInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10001',
        )

        with pytest.raises(ValueError, match='only valid in UPDATE mode'):
            widget.get_value_for_update()

    @pytest.mark.asyncio
    async def test_get_value_for_create_valid_float(self, app):
        """Test get_value_for_create with valid float."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.CREATE,
                field_id='customfield_10001',
            )

            widget.value = '7.5'
            result = widget.get_value_for_create()
            assert result == 7.5

    def test_get_value_for_create_empty(self):
        """Test get_value_for_create with empty value."""
        widget = NumericInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10001',
        )

        widget.value = ''
        result = widget.get_value_for_create()
        assert result is None

    def test_get_value_for_create_wrong_mode(self):
        """Test get_value_for_create raises error in UPDATE mode."""
        widget = NumericInputWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10001',
        )

        with pytest.raises(ValueError, match='only valid in CREATE mode'):
            widget.get_value_for_create()

    @pytest.mark.asyncio
    async def test_value_has_changed_no_original(self, app):
        """Test value_has_changed when original value is None."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=None,
            )

            # No change - both empty
            widget.value = ''
            assert widget.value_has_changed is False

            # Change - now has value
            widget.value = '5.0'
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_cleared_value(self, app):
        """Test value_has_changed when value is cleared."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = ''
            assert widget.value_has_changed is True

            widget.value = '   '
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_same_value(self, app):
        """Test value_has_changed with same value."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = '5.0'
            assert widget.value_has_changed is False

            # Integer representation of same value
            widget.value = '5'
            assert widget.value_has_changed is False

    @pytest.mark.asyncio
    async def test_value_has_changed_different_value(self, app):
        """Test value_has_changed with different value."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = '7.5'
            assert widget.value_has_changed is True

    @pytest.mark.asyncio
    async def test_value_has_changed_invalid_value(self, app):
        """Test value_has_changed with invalid numeric value."""
        async with app.run_test():
            widget = NumericInputWidget(
                mode=FieldMode.UPDATE,
                field_id='customfield_10001',
                original_value=5.0,
            )

            widget.value = 'invalid'
            assert widget.value_has_changed is True

    def test_value_has_changed_wrong_mode(self):
        """Test value_has_changed raises error in CREATE mode."""
        widget = NumericInputWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10001',
        )

        with pytest.raises(ValueError, match='only valid in UPDATE mode'):
            _ = widget.value_has_changed


# ============================================================================
# Selection Widget Tests
# ============================================================================


class TestSelectionWidget:
    """Tests for SelectionWidget in both CREATE and UPDATE modes."""

    def test_create_mode_initialization(self):
        """Test SelectionWidget initialization in CREATE mode."""
        options = [('High', '1'), ('Medium', '2'), ('Low', '3')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='priority',
            options=options,
            title='Priority',
            required=False,
        )

        assert widget.mode == FieldMode.CREATE
        assert widget.field_id == 'priority'
        assert widget.border_title == 'Priority'
        assert widget.compact is True
        assert 'create-work-item-generic-selector' in widget.classes

    def test_create_mode_required_field(self):
        """Test SelectionWidget with required flag in CREATE mode."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='priority',
            options=options,
            title='Priority',
            required=True,
        )

        assert widget.border_subtitle == '(*)'
        assert 'required' in widget.classes

    def test_create_mode_with_initial_value(self):
        """Test SelectionWidget with initial value in CREATE mode."""
        options = [('High', '1'), ('Medium', '2'), ('Low', '3')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='priority',
            options=options,
            initial_value='2',
        )

        assert widget.value == '2'

    def test_update_mode_initialization(self):
        """Test SelectionWidget initialization in UPDATE mode."""
        options = [('High', '1'), ('Medium', '2'), ('Low', '3')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            title='Priority',
            original_value='2',
            field_supports_update=True,
        )

        assert widget.mode == FieldMode.UPDATE
        assert widget.field_id == 'customfield_10002'
        assert widget.jira_field_key == 'customfield_10002'
        assert widget.original_value == '2'
        assert widget.value == '2'
        assert widget.disabled is False
        assert 'create-work-item-generic-selector' in widget.classes

    def test_update_mode_disabled_field(self):
        """Test SelectionWidget with update disabled."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value='2',
            field_supports_update=False,
        )

        assert widget.disabled is True

    def test_update_mode_none_original_value(self):
        """Test SelectionWidget with None original value."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value=None,
        )

        assert widget.original_value is None

    def test_get_value_for_update_with_selection(self):
        """Test get_value_for_update with valid selection."""
        options = [('High', '1'), ('Medium', '2'), ('Low', '3')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value='2',
        )

        widget.value = '3'
        result = widget.get_value_for_update()
        assert result == {'id': '3'}

    def test_get_value_for_update_no_selection(self):
        """Test get_value_for_update with no selection."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value='2',
        )

        # Simulate no selection (selection property is None)
        widget.value = Select.BLANK
        result = widget.get_value_for_update()
        assert result is None

    def test_get_value_for_update_wrong_mode(self):
        """Test get_value_for_update raises error in CREATE mode."""
        options = [('High', '1')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            options=options,
        )

        with pytest.raises(ValueError, match='only valid in UPDATE mode'):
            widget.get_value_for_update()

    def test_get_value_for_create_with_selection(self):
        """Test get_value_for_create with valid selection."""
        options = [('High', '1'), ('Medium', '2'), ('Low', '3')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            options=options,
        )

        widget.value = '3'
        result = widget.get_value_for_create()
        assert result == {'id': '3'}

    def test_get_value_for_create_no_selection(self):
        """Test get_value_for_create with no selection."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            options=options,
        )

        widget.value = Select.BLANK
        result = widget.get_value_for_create()
        assert result is None

    def test_get_value_for_create_wrong_mode(self):
        """Test get_value_for_create raises error in UPDATE mode."""
        options = [('High', '1')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
        )

        with pytest.raises(ValueError, match='only valid in CREATE mode'):
            widget.get_value_for_create()

    def test_value_has_changed_no_original(self):
        """Test value_has_changed when original value is None."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value=None,
        )

        # No change - both empty
        widget.value = Select.BLANK
        assert widget.value_has_changed is False

        # Change - now has selection
        widget.value = '1'
        assert widget.value_has_changed is True

    def test_value_has_changed_cleared_selection(self):
        """Test value_has_changed when selection is cleared."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value='2',
        )

        widget.value = Select.BLANK
        assert widget.value_has_changed is True

    def test_value_has_changed_same_value(self):
        """Test value_has_changed with same value."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value='2',
        )

        widget.value = '2'
        assert widget.value_has_changed is False

    def test_value_has_changed_different_value(self):
        """Test value_has_changed with different value."""
        options = [('High', '1'), ('Medium', '2'), ('Low', '3')]
        widget = SelectionWidget(
            mode=FieldMode.UPDATE,
            field_id='customfield_10002',
            options=options,
            original_value='2',
        )

        widget.value = '3'
        assert widget.value_has_changed is True

    def test_value_has_changed_wrong_mode(self):
        """Test value_has_changed raises error in CREATE mode."""
        options = [('High', '1')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            options=options,
        )

        with pytest.raises(ValueError, match='only valid in UPDATE mode'):
            _ = widget.value_has_changed

    def test_custom_prompt(self):
        """Test SelectionWidget with custom prompt."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            options=options,
            prompt='Choose a value',
        )

        assert widget.prompt == 'Choose a value'

    def test_default_prompt_generation(self):
        """Test SelectionWidget default prompt generation."""
        options = [('High', '1'), ('Medium', '2')]
        widget = SelectionWidget(
            mode=FieldMode.CREATE,
            field_id='customfield_10002',
            options=options,
            title='Priority',
        )

        assert widget.prompt == 'Select Priority'


# ============================================================================
# Widget Inheritance Tests
# ============================================================================


class TestWidgetInheritance:
    """Tests to verify correct inheritance and base class behavior."""

    def test_date_widget_extends_date_input(self):
        """Test that DateInputWidget extends DateInput (MaskedInput)."""
        widget = DateInputWidget(
            mode=FieldMode.CREATE,
            field_id='test',
        )

        assert isinstance(widget, MaskedInput)
        assert hasattr(widget, 'template')
        assert widget.template == '9999-99-99'

    def test_datetime_widget_extends_masked_input(self):
        """Test that DateTimeInputWidget extends MaskedInput."""
        widget = DateTimeInputWidget(
            mode=FieldMode.CREATE,
            field_id='test',
        )

        assert isinstance(widget, MaskedInput)
        assert widget.template == '9999-99-99 99:99:99'

    def test_text_widget_extends_input(self):
        """Test that TextInputWidget extends Input."""
        widget = TextInputWidget(
            mode=FieldMode.CREATE,
            field_id='test',
        )

        assert isinstance(widget, Input)
        assert hasattr(widget, 'value')
