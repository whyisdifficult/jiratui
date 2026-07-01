from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest
from textual.widgets import Rule, Static

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.app import JiraApp
from jiratui.exceptions import UpdateWorkItemException, ValidationError
from jiratui.models import JiraIssue
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.commons.factory_utils import build_read_only_rich_text_widget
from jiratui.widgets.work_item_info.info import (
    WorkItemInfoContainer,
)
from jiratui.widgets.work_item_info.tabs import InfoTabbedContent, TextAreaTabPane


@pytest.mark.asyncio
async def test_work_item_info_container_with_summary_description_only(
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
                'name': 'description',
                'required': True,
            },
        }
    }
    jira_issues_with_custom_fields[0].description = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert isinstance(widget.info_tabbed_content, InfoTabbedContent)
        tab_panes = widget.info_tabbed_content.query(TextAreaTabPane)
        assert len(tab_panes) == 1
        assert isinstance(tab_panes[0], TextAreaTabPane)
        assert tab_panes[0].id == 'pane-description'
        assert isinstance(tab_panes[0].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert tab_panes[0].children[0].border_title == 'Description'
        assert tab_panes[0].children[0].border_subtitle == '(*)'
        assert tab_panes[0].children[0].jira_field_key == 'description'


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@patch.object(
    WorkItemInfoContainer, '_enable_updating_additional_fields', PropertyMock(return_value=True)
)
@pytest.mark.asyncio
async def test_work_item_info_container_updating_additional_fields_enabled(
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
                'name': 'description',
                'required': True,
            },
            'environment': {
                'schema': {'custom': ''},
                'key': 'environment',
                'name': 'environment',
                'required': True,
            },
            'field_a': {
                'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'},
                'key': 'field_a',
                'name': 'Field A',
                'required': False,
            },
        }
    }
    jira_issues_with_custom_fields[0].description = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    jira_issues_with_custom_fields[0].environment = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Goodbye world!'}]}],
    }
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert isinstance(widget.info_tabbed_content, InfoTabbedContent)
        tab_panes = widget.info_tabbed_content.query(TextAreaTabPane)
        assert len(tab_panes) == 3
        assert isinstance(tab_panes[0], TextAreaTabPane)
        assert isinstance(tab_panes[1], TextAreaTabPane)
        assert isinstance(tab_panes[2], TextAreaTabPane)
        assert tab_panes[0].id == 'pane-description'
        assert tab_panes[1].id == 'pane-environment'
        assert isinstance(tab_panes[0].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert isinstance(tab_panes[1].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert isinstance(tab_panes[2].children[0], Static)
        assert tab_panes[0].children[0].border_title == 'Description'
        assert tab_panes[0].children[0].border_subtitle == '(*)'
        assert tab_panes[0].children[0].jira_field_key == 'description'
        assert tab_panes[1].children[0].border_title == 'environment'
        assert tab_panes[1].children[0].border_subtitle == '(*)'
        assert tab_panes[1].children[0].jira_field_key == 'environment'


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@patch.object(
    WorkItemInfoContainer, '_enable_updating_additional_fields', PropertyMock(return_value=False)
)
@pytest.mark.asyncio
async def test_work_item_info_container_updating_additional_fields_disabled(
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
                'name': 'description',
                'required': True,
            },
            'environment': {
                'schema': {'custom': ''},
                'key': 'environment',
                'name': 'environment',
                'required': True,
            },
        }
    }
    jira_issues_with_custom_fields[0].description = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    jira_issues_with_custom_fields[0].environment = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Goodbye world!'}]}],
    }
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert isinstance(widget.info_tabbed_content, InfoTabbedContent)
        tab_panes = widget.info_tabbed_content.query(TextAreaTabPane)
        assert len(tab_panes) == 1
        assert isinstance(tab_panes[0], TextAreaTabPane)
        assert tab_panes[0].id == 'pane-description'
        assert isinstance(tab_panes[0].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert tab_panes[0].children[0].border_title == 'Description'
        assert tab_panes[0].children[0].border_subtitle == '(*)'
        assert tab_panes[0].children[0].jira_field_key == 'description'


@patch.object(
    WorkItemInfoContainer,
    '_update_additional_fields_ignore_ids',
    PropertyMock(return_value=['environment']),
)
@patch.object(
    WorkItemInfoContainer, '_enable_updating_additional_fields', PropertyMock(return_value=False)
)
@pytest.mark.asyncio
async def test_work_item_info_container_updating_additional_fields_enabled_with_ignore_list(
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
                'name': 'description',
                'required': True,
            },
            'environment': {
                'schema': {'custom': ''},
                'key': 'environment',
                'name': 'environment',
                'required': True,
            },
        }
    }
    jira_issues_with_custom_fields[0].description = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    jira_issues_with_custom_fields[0].environment = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Goodbye world!'}]}],
    }
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert isinstance(widget.info_tabbed_content, InfoTabbedContent)
        tab_panes = widget.info_tabbed_content.query(TextAreaTabPane)
        assert len(tab_panes) == 1
        assert isinstance(tab_panes[0], TextAreaTabPane)
        assert tab_panes[0].id == 'pane-description'
        assert isinstance(tab_panes[0].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert tab_panes[0].children[0].border_title == 'Description'
        assert tab_panes[0].children[0].border_subtitle == '(*)'
        assert tab_panes[0].children[0].jira_field_key == 'description'


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@patch.object(
    WorkItemInfoContainer, '_enable_updating_additional_fields', PropertyMock(return_value=True)
)
@pytest.mark.asyncio
async def test_work_item_info_container_updating_additional_fields_enable_with_textarea_custom_type(
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
                'name': 'description',
                'required': True,
            },
            'environment': {
                'schema': {'custom': ''},
                'key': 'environment',
                'name': 'environment',
                'required': True,
            },
            'field_a': {
                'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'},
                'key': 'field_a',
                'name': 'Field A',
                'required': False,
            },
        }
    }
    jira_issues_with_custom_fields[0].description = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    jira_issues_with_custom_fields[0].environment = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Goodbye world!'}]}],
    }
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert isinstance(widget.info_tabbed_content, InfoTabbedContent)
        tab_panes = widget.info_tabbed_content.query(TextAreaTabPane)
        assert len(tab_panes) == 3
        assert isinstance(tab_panes[0], TextAreaTabPane)
        assert isinstance(tab_panes[1], TextAreaTabPane)
        assert isinstance(tab_panes[2], TextAreaTabPane)
        assert tab_panes[0].id == 'pane-description'
        assert tab_panes[1].id == 'pane-environment'
        assert tab_panes[2].id == 'pane-field_a'
        assert isinstance(tab_panes[0].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert isinstance(tab_panes[1].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert isinstance(tab_panes[2].children[0], Static)
        assert tab_panes[0].children[0].border_title == 'Description'
        assert tab_panes[0].children[0].border_subtitle == '(*)'
        assert tab_panes[0].children[0].jira_field_key == 'description'
        assert tab_panes[1].children[0].border_title == 'environment'
        assert tab_panes[1].children[0].border_subtitle == '(*)'
        assert tab_panes[1].children[0].jira_field_key == 'environment'
        assert tab_panes[2].children[0].id == 'field_a'


@pytest.mark.asyncio
async def test_work_item_info_container_with_view_content(app):
    async with app.run_test() as pilot:
        # GIVEN
        widget = InfoTabbedContent()
        await app.screen.mount(widget)
        await pilot.pause()
        pane = TextAreaTabPane(title='Description', widget_id='pane-description')
        await widget.add_pane(pane)
        await pane.mount(
            build_read_only_rich_text_widget(
                jira_field_key='description',
                field_name='Description',
                required=False,
                content={
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}
                    ],
                },
            )
        )
        # WHEN
        widget.action_view_content()
        # THEN
        assert isinstance(widget.active_pane, TextAreaTabPane)
        assert (
            widget.active_pane.query_one(ReadOnlyADFMarkdownTextAreaWidget).text_content
            == 'Hello world!\n'
        )


@patch.object(JiraApp, 'copy_to_clipboard')
@pytest.mark.asyncio
async def test_copy_content_to_clipboard(copy_to_clipboard_mock: Mock, app):
    async with app.run_test() as pilot:
        # GIVEN
        widget = InfoTabbedContent()
        await app.screen.mount(widget)
        await pilot.pause()
        pane = TextAreaTabPane(title='Description', widget_id='pane-description')
        await widget.add_pane(pane)
        await pane.mount(
            build_read_only_rich_text_widget(
                jira_field_key='description',
                field_name='Description',
                required=False,
                content={
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}
                    ],
                },
            )
        )
        # WHEN
        widget.action_copy_content()
        # THEN
        copy_to_clipboard_mock.assert_called_once_with('Hello world!')


@pytest.mark.asyncio
async def test_build_textarea_widgets_without_edit_metadata(jira_issues_with_custom_fields, app):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {}
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert widgets == []


@pytest.mark.asyncio
async def test_build_textarea_widgets_without_edit_metadata_fields(
    jira_issues_with_custom_fields, app
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {'fields': {}}
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert widgets == []


@patch.object(
    WorkItemInfoContainer,
    '_update_additional_fields_ignore_ids',
    PropertyMock(return_value=['field_a']),
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_with_ignored_fields(jira_issues_with_custom_fields, app):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {'fields': {'field_a': {'key': 'field_a'}}}
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert widgets == []


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_skip_description(jira_issues_with_custom_fields, app):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {'description': {'key': 'description'}}
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert widgets == []


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_skip_fields_without_schema(
    jira_issues_with_custom_fields, app
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {'fields': {'field_a': {'key': 'field_a'}}}
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert widgets == []


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_skip_fields_with_non_textarea_schema(
    jira_issues_with_custom_fields, app
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {'field_a': {'key': 'field_a', 'schema': {'custom': 'custom-type'}}}
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert widgets == []


@patch.object(JiraIssue, 'get_custom_field_value')
@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_with_empty_field_value_generates_static(
    get_custom_field_value_mock: Mock, jira_issues_with_custom_fields, app
):
    # GIVEN
    get_custom_field_value_mock.return_value = ''
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'field_a': {
                'key': 'field_a',
                'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'},
            }
        }
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert isinstance(widgets[0], Static)
        assert len(widgets) == 1
        assert widgets[0].id == 'field_a'
        assert widgets[0].name == 'Field A'


@patch('jiratui.widgets.work_item_info.info.build_read_only_rich_text_widget')
@patch.object(JiraIssue, 'get_custom_field_value')
@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_with_non_empty_field_value_generates_adf_widget(
    get_custom_field_value_mock: Mock,
    build_read_only_rich_text_widget_mock: Mock,
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    get_custom_field_value_mock.return_value = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    build_read_only_rich_text_widget_mock.return_value = ReadOnlyADFMarkdownTextAreaWidget(
        jira_field_key='field_a',
        field_id='field_a',
        title='Field A',
    )
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'field_a': {
                'key': 'field_a',
                'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'},
            }
        }
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert isinstance(widgets[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert len(widgets) == 1
        assert widgets[0].id == 'field_a'
        assert widgets[0].jira_field_key == 'field_a'
        assert widgets[0].field_title == 'Field A'


@patch.object(JiraIssue, 'get_custom_field_value')
@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_with_empty_environment_field_value_generates_static(
    get_custom_field_value_mock: Mock, jira_issues_with_custom_fields, app
):
    # GIVEN
    get_custom_field_value_mock.return_value = ''
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {'environment': {'key': 'environment', 'schema': {'custom': 'custom-type'}}}
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert isinstance(widgets[0], Static)
        assert len(widgets) == 1
        assert widgets[0].id == 'environment'
        assert widgets[0].name == 'Environment'


@patch('jiratui.widgets.work_item_info.info.build_read_only_rich_text_widget')
@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@pytest.mark.asyncio
async def test_build_textarea_widgets_with_non_empty_environment_field_value_generates_adf_widget(
    build_read_only_rich_text_widget_mock: Mock, jira_issues_with_custom_fields, app
):
    # GIVEN
    jira_issues_with_custom_fields[0].environment = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    build_read_only_rich_text_widget_mock.return_value = ReadOnlyADFMarkdownTextAreaWidget(
        jira_field_key='environment',
        field_id='environment',
        title='environment',
    )
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {'environment': {'key': 'environment', 'schema': {'custom': 'custom-type'}}}
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widgets = widget._build_textarea_widgets(jira_issues_with_custom_fields[0])
        # THEN
        assert isinstance(widgets[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert len(widgets) == 1
        assert widgets[0].id == 'environment'
        assert widgets[0].jira_field_key == 'environment'
        assert widgets[0].field_title == 'environment'


@pytest.mark.asyncio
async def test_work_item_info_container_clear_information(
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    jira_issues_with_custom_fields[0].edit_meta = {
        'fields': {
            'description': {
                'key': 'description',
                'name': 'description',
                'required': True,
            },
        }
    }
    jira_issues_with_custom_fields[0].description = {
        'type': 'doc',
        'version': 1,
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world!'}]}],
    }
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert isinstance(widget.info_tabbed_content, InfoTabbedContent)
        tab_panes = widget.info_tabbed_content.query(TextAreaTabPane)
        assert len(tab_panes) == 1
        assert isinstance(tab_panes[0], TextAreaTabPane)
        assert tab_panes[0].id == 'pane-description'
        assert isinstance(tab_panes[0].children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert tab_panes[0].children[0].border_title == 'Description'
        # WHEN
        widget.clear_information = True
        await app.workers.wait_for_complete()
        # THEN
        assert widget.issue_summary_widget.content == ''
        assert widget.issue_summary_widget.visible is False
        assert widget.query_one(Rule).visible is False
        assert (
            widget.query_one_optional('#info-tabbed-content', expect_type=InfoTabbedContent) is None
        )
        assert len(widget.tabs_container.children) == 0


@patch.object(WorkItemInfoContainer, 'run_worker')
@pytest.mark.asyncio
async def test_handle_edit_result_schedules_update(run_worker_mock: Mock, app):
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        data = {'jira_field_key': 'description', 'content': 'updated text'}
        widget._handle_edit_result(data)
        run_worker_mock.assert_called_once_with(widget._update_field(data))


@patch.object(WorkItemInfoContainer, 'run_worker')
@pytest.mark.asyncio
async def test_handle_edit_result_without_field_key_shows_error(run_worker_mock: Mock, app):
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        widget._handle_edit_result({'content': 'updated text'})
        run_worker_mock.assert_not_called()


@patch.object(WorkItemInfoContainer, '_send_work_item_updated_message')
@patch.object(APIController, 'update_issue')
@pytest.mark.parametrize(
    'update_field_data, expected_result',
    [({}, None), ({'jira_field_key': ''}, None), ({'field': '1'}, None)],
)
@pytest.mark.asyncio
async def test_update_field_data_parameter(
    update_issue_mock: AsyncMock,
    send_work_item_updated_message_mock: Mock,
    update_field_data,
    expected_result,
    app,
):
    # GIVEN
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue = None
        await app.workers.wait_for_complete()
        await pilot.pause()
        # WHEN
        result = await widget._update_field(update_field_data)  # type:ignore[func-returns-value]
        # THEN
        assert result == expected_result
        update_issue_mock.assert_not_called()
        send_work_item_updated_message_mock.assert_not_called()


@patch.object(WorkItemInfoContainer, '_send_work_item_updated_message')
@patch.object(APIController, 'update_issue')
@patch.object(
    WorkItemInfoContainer, '_updating_rich_text_is_enabled', PropertyMock(return_value=False)
)
@pytest.mark.asyncio
async def test_update_field_updating_rich_text_is_enabled_false(
    update_issue_mock: AsyncMock,
    send_work_item_updated_message_mock: Mock,
    app,
):
    # GIVEN
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue = None
        await app.workers.wait_for_complete()
        await pilot.pause()
        # WHEN
        result = await widget._update_field({'jira_field_key': 'description', 'content': 'abcd'})  # type:ignore[func-returns-value]
        # THEN
        assert result is None
        update_issue_mock.assert_not_called()
        send_work_item_updated_message_mock.assert_not_called()


@patch.object(WorkItemInfoContainer, '_send_work_item_updated_message')
@patch.object(APIController, 'update_issue')
@patch.object(
    WorkItemInfoContainer, '_updating_rich_text_is_enabled', PropertyMock(return_value=True)
)
@pytest.mark.asyncio
async def test_update_field_updating_rich_text_is_enabled_true(
    update_issue_mock: AsyncMock,
    send_work_item_updated_message_mock: Mock,
    jira_issues_with_custom_fields,
    app,
):
    # GIVEN
    update_issue_mock.return_value = APIControllerResponse(success=True)
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        # WHEN
        result = await widget._update_field({'jira_field_key': 'description', 'content': 'abcd'})  # type:ignore[func-returns-value]
        # THEN
        assert result is None
        update_issue_mock.assert_called_once_with(
            jira_issues_with_custom_fields[0], {'description': 'abcd'}
        )
        send_work_item_updated_message_mock.assert_called_once()


@pytest.mark.parametrize('error_type', [UpdateWorkItemException(), ValidationError(), ValueError()])
@patch.object(WorkItemInfoContainer, '_send_work_item_updated_message')
@patch.object(APIController, 'update_issue')
@patch.object(
    WorkItemInfoContainer, '_updating_rich_text_is_enabled', PropertyMock(return_value=True)
)
@pytest.mark.asyncio
async def test_update_field_update_issue_raises_error(
    update_issue_mock: AsyncMock,
    send_work_item_updated_message_mock: Mock,
    jira_issues_with_custom_fields,
    error_type,
    app,
):
    # GIVEN
    update_issue_mock.side_effect = error_type
    async with app.run_test() as pilot:
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        await app.workers.wait_for_complete()
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        await pilot.pause()
        # WHEN
        result = await widget._update_field({'jira_field_key': 'description', 'content': 'abcd'})  # type:ignore[func-returns-value]
        # THEN
        assert result is None
        update_issue_mock.assert_called_once_with(
            jira_issues_with_custom_fields[0], {'description': 'abcd'}
        )
        send_work_item_updated_message_mock.assert_not_called()
