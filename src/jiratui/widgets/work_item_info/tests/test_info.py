from unittest.mock import PropertyMock, patch

import pytest
from textual.widgets import Rule

from jiratui.widgets.commons import FieldMode
from jiratui.widgets.commons.adf import ADFTextAreaWidget
from jiratui.widgets.work_item_info.info import (
    TextareaCollapsible,
    WorkItemInfoContainer,
)


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
            }
        }
    }
    async with app.run_test():
        widget = WorkItemInfoContainer()
        await app.screen.mount(widget)
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert len(widget.collapsible_container.children) == 1


@patch.object(
    WorkItemInfoContainer, '_update_additional_fields_ignore_ids', PropertyMock(return_value=[])
)
@patch.object(
    WorkItemInfoContainer, '_enable_updating_additional_fields', PropertyMock(return_value=True)
)
@pytest.mark.asyncio
async def test_work_item_info_container_updating_additional_fields_enable(
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
    async with app.run_test():
        widget = WorkItemInfoContainer()

        await app.screen.mount(widget)
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert len(widget.collapsible_container.children) == 2
        assert isinstance(widget.collapsible_container.children[0], TextareaCollapsible)
        assert isinstance(widget.collapsible_container.children[1], TextareaCollapsible)
        keys = [w._jira_field_key for w in widget.collapsible_container.children]
        assert 'environment' in keys
        assert 'description' in keys


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
    async with app.run_test():
        widget = WorkItemInfoContainer()

        await app.screen.mount(widget)
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert len(widget.collapsible_container.children) == 1
        assert isinstance(widget.collapsible_container.children[0], TextareaCollapsible)
        keys = [w._jira_field_key for w in widget.collapsible_container.children]
        assert 'description' in keys
        assert 'environment' not in keys


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
    async with app.run_test():
        widget = WorkItemInfoContainer()

        await app.screen.mount(widget)
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert len(widget.collapsible_container.children) == 1
        assert isinstance(widget.collapsible_container.children[0], TextareaCollapsible)
        keys = [w._jira_field_key for w in widget.collapsible_container.children]
        assert 'description' in keys
        assert 'environment' not in keys


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
    async with app.run_test():
        widget = WorkItemInfoContainer()

        await app.screen.mount(widget)
        # WHEN
        widget.issue = jira_issues_with_custom_fields[0]
        await app.workers.wait_for_complete()
        assert widget.issue_summary_widget.content == 'abcd'
        assert widget.query_one(Rule).visible is True
        assert len(widget.collapsible_container.children) == 3
        assert isinstance(widget.collapsible_container.children[0], TextareaCollapsible)
        assert isinstance(widget.collapsible_container.children[1], TextareaCollapsible)
        assert isinstance(widget.collapsible_container.children[2], TextareaCollapsible)
        keys = [w._jira_field_key for w in widget.collapsible_container.children]
        assert 'environment' in keys
        assert 'description' in keys
        assert 'field_a' in keys
        assert widget.collapsible_container.children[2].border_subtitle == '(*)'
        assert widget.collapsible_container.children[1].border_subtitle is None


@pytest.mark.asyncio
async def test_work_item_info_container_with_view_content(app):
    # GIVEN
    async with app.run_test() as pilot:
        widget = TextareaCollapsible(
            'description',
            'description',
            ADFTextAreaWidget(
                mode=FieldMode.UPDATE,
                jira_field_key='description',
                field_id='description',
                original_value={
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                },
            ),
        )
        await app.screen.mount(widget)
        await pilot.pause()
        # WHEN
        widget.action_view_content()
        # THEN
        assert isinstance(widget.widget, ADFTextAreaWidget)
        assert widget.text_content == 'Hello world\n'
