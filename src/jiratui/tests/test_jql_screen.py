from unittest.mock import Mock, PropertyMock, patch

import pytest
from textual.widgets import TextArea

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import JiraFilter
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


@patch.object(APIController, 'get_favourite_filters')
@patch.object(JQLEditorScreen, '_show_favourite_filters', PropertyMock(return_value=False))
@patch.object(
    JQLEditorScreen,
    '_pre_defined_jql_expressions',
    PropertyMock(return_value={'1': {'label': 'Expression A', 'expression': 'expression 1'}}),
)
@pytest.mark.asyncio
async def test_open_jql_editor_screen_does_not_fetch_favourite_filters_when_disabled(
    get_favourite_filters_mock: Mock, app
):
    # GIVEN
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen()
        await app.push_screen(screen)
        await pilot.pause()
        # THEN
        get_favourite_filters_mock.assert_not_called()
        assert screen.favourite_filters == {}
        widget = screen.query_one(PreDefinedJQLExpressionsWidget)
        assert [option[1] for option in widget._options if option[1] != widget.NULL] == ['1']


@patch.object(APIController, 'get_favourite_filters')
@patch.object(JQLEditorScreen, '_show_favourite_filters', PropertyMock(return_value=True))
@patch.object(
    JQLEditorScreen,
    '_pre_defined_jql_expressions',
    PropertyMock(return_value={'1': {'label': 'Expression A', 'expression': 'expression 1'}}),
)
@pytest.mark.asyncio
async def test_open_jql_editor_screen_with_favourite_filters_select_filter(
    get_favourite_filters_mock: Mock, app
):
    # GIVEN
    get_favourite_filters_mock.return_value = APIControllerResponse(
        result=[
            JiraFilter(id='10000', name='Not done', jql='statusCategory != Done'),
            JiraFilter(id='10001', name='No JQL', jql=None),
        ]
    )
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen()
        await app.push_screen(screen)
        await pilot.pause()
        await screen.workers.wait_for_complete()
        await pilot.pause()
        # THEN
        get_favourite_filters_mock.assert_called_once_with()
        widget = screen.query_one(PreDefinedJQLExpressionsWidget)
        assert [option for option in widget._options if option[1] != widget.NULL] == [
            ('Expression A', '1'),
            ('★ Not done', 'jira-filter-10000'),
            ('★ No JQL', 'jira-filter-10001'),
        ]
        textarea = screen.query_one(TextArea)
        widget.value = 'jira-filter-10000'
        await pilot.pause()
        assert textarea.text == 'statusCategory != Done'
        widget.value = 'jira-filter-10001'
        await pilot.pause()
        assert textarea.text == 'filter = 10001'
        widget.value = '1'
        await pilot.pause()
        assert textarea.text == 'expression 1'


@patch.object(APIController, 'get_favourite_filters')
@patch.object(JQLEditorScreen, '_show_favourite_filters', PropertyMock(return_value=True))
@patch.object(JQLEditorScreen, '_pre_defined_jql_expressions', PropertyMock(return_value=None))
@pytest.mark.asyncio
async def test_open_jql_editor_screen_with_favourite_filters_api_error(
    get_favourite_filters_mock: Mock, app
):
    # GIVEN
    get_favourite_filters_mock.return_value = APIControllerResponse(
        success=False, error='some error'
    )
    async with app.run_test() as pilot:
        # WHEN
        screen = JQLEditorScreen('some content')
        screen.notify = Mock()
        await app.push_screen(screen)
        await pilot.pause()
        await screen.workers.wait_for_complete()
        await pilot.pause()
        # THEN
        assert screen.favourite_filters == {}
        screen.notify.assert_called_once()
        assert 'some error' in screen.notify.call_args[0][0]
        assert screen.query_one(TextArea).text == 'some content'
