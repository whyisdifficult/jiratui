from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from textual.widgets import DataTable, Static, TabPane

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.models import IssueStatus, IssueType, JiraIssue, JiraIssueSearchResponse, Project
from jiratui.widgets.commons.adf import ReadOnlyADFMarkdownTextAreaWidget
from jiratui.widgets.work_item_details.read_only_details import WorkItemReadOnlyDetailsScreen


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_read_only_details_without_description(
    get_issue_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    work_item.description = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    async with app.run_test():
        screen = WorkItemReadOnlyDetailsScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        dt = screen.query_one(DataTable)
        assert dt.row_count == 13
        tab_description = screen.query_one('#tab-description', expect_type=TabPane)
        assert isinstance(tab_description.children[0], Static)
        assert tab_description.children[0].content == 'There is no Description set.'


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_read_only_details_with_description(
    get_issue_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    work_item.description = {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'content': [{'type': 'text', 'text': 'Some value for the ADF field'}],
                'type': 'paragraph',
            }
        ],
    }
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[jira_issues[1]])
    )
    async with app.run_test():
        screen = WorkItemReadOnlyDetailsScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        dt = screen.query_one(DataTable)
        assert dt.row_count == 13
        tab_description = screen.query_one('#tab-description', expect_type=TabPane)
        assert isinstance(tab_description.children[0], ReadOnlyADFMarkdownTextAreaWidget)
        assert tab_description.children[0].text_content == 'Some value for the ADF field\n'


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_read_only_details_without_description_without_edit_metadata(
    get_issue_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = jira_issues[1]
    work_item.description = None
    work_item.edit_metadata = None
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    async with app.run_test():
        screen = WorkItemReadOnlyDetailsScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        dt = screen.query_one(DataTable)
        assert dt.row_count == 13
        tab_description = screen.query_one('#tab-description', expect_type=TabPane)
        assert isinstance(tab_description.children[0], Static)


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_read_only_details_without_description_with_edit_metadata(
    get_issue_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = JiraIssue(
        id='1',
        key='WI-1',
        summary='abcd',
        description='',
        project=Project(id='2', name='Project 2', key='P2'),
        created=datetime(2025, 10, 31),
        updated=datetime(2025, 10, 31),
        status=IssueStatus(name='Done', id='1'),
        issue_type=IssueType(id='1', name='Task'),
        edit_meta={
            'fields': {
                'field_a': {
                    'schema': {
                        'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'
                    },
                    'key': 'field_a',
                    'name': 'Field A',
                    'required': False,
                },
            }
        },
        custom_fields={
            'field_a': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {
                        'content': [{'type': 'text', 'text': 'Some value for the ADF field'}],
                        'type': 'paragraph',
                    }
                ],
            },
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    async with app.run_test():
        screen = WorkItemReadOnlyDetailsScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        dt = screen.query_one(DataTable)
        assert dt.row_count == 13
        tab_description = screen.query_one('#tab-description', expect_type=TabPane)
        assert isinstance(tab_description.children[0], Static)
        tab = screen.query_one('#tab-field_a', expect_type=TabPane)
        assert isinstance(tab.children[0], ReadOnlyADFMarkdownTextAreaWidget)


@patch.object(APIController, 'get_issue')
@pytest.mark.asyncio
async def test_read_only_details_without_description_with_edit_metadata_without_field_value(
    get_issue_mock: AsyncMock,
    jira_issues,
    app,
):
    # GIVEN
    work_item = JiraIssue(
        id='1',
        key='WI-1',
        summary='abcd',
        description='',
        project=Project(id='2', name='Project 2', key='P2'),
        created=datetime(2025, 10, 31),
        updated=datetime(2025, 10, 31),
        status=IssueStatus(name='Done', id='1'),
        issue_type=IssueType(id='1', name='Task'),
        edit_meta={
            'fields': {
                'field_a': {
                    'schema': {
                        'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'
                    },
                    'key': 'field_a',
                    'name': 'Field A',
                    'required': False,
                },
            }
        },
        custom_fields={
            'field_a': None,
        },
    )
    get_issue_mock.return_value = APIControllerResponse(
        result=JiraIssueSearchResponse(issues=[work_item])
    )
    async with app.run_test():
        screen = WorkItemReadOnlyDetailsScreen('WI-1')
        # WHEN
        await app.push_screen(screen)
        await app.workers.wait_for_complete()
        # THEN
        dt = screen.query_one(DataTable)
        assert dt.row_count == 13
        tab_description = screen.query_one('#tab-description', expect_type=TabPane)
        assert isinstance(tab_description.children[0], Static)
        tab = screen.query_one('#tab-field_a', expect_type=TabPane)
        assert isinstance(tab.children[0], Static)
        assert tab.children[0].content == 'There is no "Field A" set.'
