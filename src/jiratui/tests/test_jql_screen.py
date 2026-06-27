from unittest.mock import Mock, PropertyMock, patch

import pytest
from textual.widgets import TextArea

from jiratui.widgets.screen import MainScreen
from jiratui.widgets.screens.jql import JQLEditorScreen, PreDefinedJQLExpressionsWidget


@patch.object(JQLEditorScreen, '_pre_defined_jql_expressions', PropertyMock(return_value=None))
@pytest.mark.asyncio
async def test_open_jql_editor_screen_without_predefined_expressions(app):
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen('some content')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        assert isinstance(app.screen, JQLEditorScreen)
        widget = screen.query_one(PreDefinedJQLExpressionsWidget)
        assert screen.expressions == []
        assert widget.selection is None
        textarea = screen.query_one(TextArea)
        assert textarea.text == 'some content'


@patch.object(
    JQLEditorScreen,
    '_pre_defined_jql_expressions',
    PropertyMock(
        return_value={
            '1': {'label': 'Expression A', 'expression': 'expression 1'},
            '2': {'label': 'Expression B', 'expression': 'expression 2'},
        }
    ),
)
@pytest.mark.asyncio
async def test_open_jql_editor_screen_with_predefined_expressions(app):
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen('some content')
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        assert isinstance(app.screen, JQLEditorScreen)
        widget = screen.query_one(PreDefinedJQLExpressionsWidget)
        assert screen.expressions == [
            ('1', {'label': 'Expression A', 'expression': 'expression 1'}),
            ('2', {'label': 'Expression B', 'expression': 'expression 2'}),
        ]
        assert widget.selection is None
        textarea = screen.query_one(TextArea)
        assert textarea.text == 'some content'


@patch.object(JQLEditorScreen, '_pre_defined_jql_expressions', PropertyMock(return_value=None))
@pytest.mark.asyncio
async def test_open_jql_editor_screen_without_initial_content(app):
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen()
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        assert isinstance(app.screen, JQLEditorScreen)
        widget = screen.query_one(PreDefinedJQLExpressionsWidget)
        assert screen.expressions == []
        assert widget.selection is None
        textarea = screen.query_one(TextArea)
        assert textarea.text == ''


@pytest.mark.parametrize(
    'input_message, expected_message',
    [
        ('a', 'a'),
        ('', ''),
    ],
)
@patch.object(JQLEditorScreen, '_pre_defined_jql_expressions', PropertyMock(return_value=None))
@pytest.mark.asyncio
async def test_dismiss_jql_editor_screen_with_content(input_message, expected_message, app):
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen()
        screen.dismiss = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await pilot.press('tab')
        await pilot.press(input_message)
        await pilot.press('escape')
        await pilot.press('escape')
        # THEN
        assert isinstance(app.screen, MainScreen)
        assert screen.dismiss.call_args[0][0] == expected_message


@patch.object(
    JQLEditorScreen,
    '_pre_defined_jql_expressions',
    PropertyMock(
        return_value={
            '1': {'label': 'Expression A', 'expression': 'expression 1'},
            '2': {'label': 'Expression B', 'expression': 'expression 2'},
        }
    ),
)
@pytest.mark.asyncio
async def test_open_jql_editor_screen_with_predefined_expressions_select_expression(app):
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen()
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        assert isinstance(app.screen, JQLEditorScreen)
        widget = screen.query_one(PreDefinedJQLExpressionsWidget)
        assert screen.expressions == [
            ('1', {'label': 'Expression A', 'expression': 'expression 1'}),
            ('2', {'label': 'Expression B', 'expression': 'expression 2'}),
        ]
        await pilot.press('enter')
        await pilot.press('down')
        await pilot.press('enter')
        assert widget.selection == '1'
        textarea = screen.query_one(TextArea)
        assert textarea.text == 'expression 1'
