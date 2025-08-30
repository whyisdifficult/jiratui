from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from jiratui.api_controller.factories import (
    build_comments,
    build_issue_instance,
    build_related_work_items,
)
from jiratui.config import ApplicationConfiguration
from jiratui.models import (
    Attachment,
    IssueComment,
    IssuePriority,
    IssueStatus,
    IssueType,
    JiraIssue,
    JiraUser,
    Project,
    RelatedJiraIssue,
    TimeTracking,
)
from jiratui.utils.test_utilities import load_json_response


@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
    return ApplicationConfiguration(
        jira_api_username='foo',
        jira_api_token='12345',
        jira_api_base_url='foo.bar',
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        custom_field_id_sprint='123',
    )


@pytest.fixture
def raw_comments() -> list[dict]:
    return [
        {
            'id': '1',
            'created': '2025-12-30T18:00:00',
            'updated': '2025-12-30T18:01:00',
            'author': {
                'displayName': 'Bart Simpson',
                'accountId': '1',
                'active': True,
                'emailAddress': 'bart@simpson.com',
            },
            'updateAuthor': {
                'displayName': 'Lisa Simpson',
                'accountId': '2',
                'active': True,
                'emailAddress': 'lisa@simpson.com',
            },
            'body': {'text': 'hello world'},
        },
        {
            'id': '2',
            'created': '2025-12-10T18:00:00',
            'updated': '2025-12-10T18:01:00',
            'author': {
                'displayName': 'Homer Simpson',
                'accountId': '3',
                'active': True,
                'emailAddress': 'homer@simpson.com',
            },
            'updateAuthor': {
                'displayName': 'Maggie Simpson',
                'accountId': '4',
                'active': True,
                'emailAddress': 'maggie@simpson.com',
            },
            'body': {'text': 'hello'},
        },
    ]


def test_build_comments(raw_comments):
    # WHEN
    comments = build_comments(raw_comments)
    # THEN
    assert comments == [
        IssueComment(
            id='1',
            author=JiraUser(
                account_id='1',
                active=True,
                display_name='Bart Simpson',
                email='bart@simpson.com',
            ),
            created=datetime(2025, 12, 30, 18, 0, 00),
            updated=datetime(2025, 12, 30, 18, 1, 00),
            update_author=JiraUser(
                account_id='2',
                active=True,
                display_name='Lisa Simpson',
                email='lisa@simpson.com',
            ),
            body='{"text": "hello world"}',
        ),
        IssueComment(
            id='2',
            author=JiraUser(
                account_id='3',
                active=True,
                display_name='Homer Simpson',
                email='homer@simpson.com',
            ),
            created=datetime(2025, 12, 10, 18, 0, 00),
            updated=datetime(2025, 12, 10, 18, 1, 00),
            update_author=JiraUser(
                account_id='4',
                active=True,
                display_name='Maggie Simpson',
                email='maggie@simpson.com',
            ),
            body='{"text": "hello"}',
        ),
    ]


def test_build_comments_with_error(raw_comments: list[dict]):
    # GIVEN
    raw_comments[0]['created'] = '1'
    # WHEN
    comments = build_comments(raw_comments)
    # THEN
    assert comments == [
        IssueComment(
            id='2',
            author=JiraUser(
                account_id='3',
                active=True,
                display_name='Homer Simpson',
                email='homer@simpson.com',
            ),
            created=datetime(2025, 12, 10, 18, 0, 00),
            updated=datetime(2025, 12, 10, 18, 1, 00),
            update_author=JiraUser(
                account_id='4',
                active=True,
                display_name='Maggie Simpson',
                email='maggie@simpson.com',
            ),
            body='{"text": "hello"}',
        ),
    ]


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_issue_instance(configuration_mock: Mock, config_for_testing):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    # WHEN
    issue = build_issue_instance(
        issue_id=work_item.get('id'),
        issue_key=work_item.get('key'),
        fields=work_item.get('fields'),
        project=work_item.get('fields').get('project'),
        reporter=work_item.get('fields').get('reporter'),
        status=work_item.get('fields').get('status'),
    )
    # THEN
    assert isinstance(issue, JiraIssue)
    assert issue == JiraIssue(
        id='10002',
        key='SCRUM-10',
        summary='(Sample) Set Up Payment Logging',
        status=IssueStatus(
            name='In Progress',
            id='10001',
        ),
        project=Project(id='10000', name='Test Project', key='SCRUM'),
        created=datetime(2025, 7, 5, 14, 34, 59),
        updated=datetime(2025, 7, 14, 22, 33, 38),
        due_date=datetime(2025, 12, 31).date(),
        reporter=JiraUser(
            account_id='abe10be',
            active=True,
            display_name='Bart',
            email='bart@simpson.com',
        ),
        issue_type=IssueType(id='10003', name='Task', scope_project=None),
        description={
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Create a logging system to store payment transaction metadata.',
                        }
                    ],
                }
            ],
        },
        attachments=[
            Attachment(
                id='2',
                filename='foo.txt',
                size=1000,
                created=datetime(2025, 12, 31),
                mime_type='text',
                author=JiraUser(
                    account_id='1',
                    active=True,
                    display_name='John Doe',
                    email='foo@bar',
                ),
            )
        ],
        time_tracking=TimeTracking(
            original_estimate='2 minutes',
            remaining_estimate='1 minute',
            time_spent='1 minute',
            original_estimate_seconds=120,
            remaining_estimate_seconds=60,
            time_spent_seconds=60,
        ),
    )


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_issue_instance_with_more_details(configuration_mock: Mock, config_for_testing):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    # WHEN
    issue = build_issue_instance(
        issue_id=work_item.get('id'),
        issue_key=work_item.get('key'),
        fields=work_item.get('fields'),
        project=work_item.get('fields').get('project'),
        reporter=work_item.get('fields').get('reporter'),
        status=work_item.get('fields').get('status'),
        priority=work_item.get('fields').get('priority'),
        assignee=work_item.get('fields').get('assignee'),
        comments=[
            IssueComment(
                id='1',
                author=JiraUser(
                    account_id='1',
                    active=True,
                    display_name='Bart Simpson',
                    email='bart@simpson.com',
                ),
                created=datetime(2025, 12, 30, 18, 0, 00),
                updated=datetime(2025, 12, 30, 18, 1, 00),
                update_author=JiraUser(
                    account_id='2',
                    active=True,
                    display_name='Lisa Simpson',
                    email='lisa@simpson.com',
                ),
                body='{"text": "hello world"}',
            )
        ],
        related_issues=[],
        parent_issue_key=work_item.get('fields').get('parent').get('key'),
        edit_meta={
            'fields': {
                'summary': {
                    'required': True,
                    'schema': {'type': 'string', 'system': 'summary'},
                    'name': 'Summary',
                    'key': 'summary',
                    'operations': ['set'],
                }
            }
        },
    )
    # THEN
    assert isinstance(issue, JiraIssue)
    assert issue == JiraIssue(
        id='10002',
        key='SCRUM-10',
        summary='(Sample) Set Up Payment Logging',
        status=IssueStatus(
            name='In Progress',
            id='10001',
        ),
        project=Project(id='10000', name='Test Project', key='SCRUM'),
        created=datetime(2025, 7, 5, 14, 34, 59),
        updated=datetime(2025, 7, 14, 22, 33, 38),
        due_date=datetime(2025, 12, 31).date(),
        reporter=JiraUser(
            account_id='abe10be',
            active=True,
            display_name='Bart',
            email='bart@simpson.com',
        ),
        issue_type=IssueType(id='10003', name='Task', scope_project=None),
        description={
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Create a logging system to store payment transaction metadata.',
                        }
                    ],
                }
            ],
        },
        attachments=[
            Attachment(
                id='2',
                filename='foo.txt',
                size=1000,
                created=datetime(2025, 12, 31),
                mime_type='text',
                author=JiraUser(
                    account_id='1',
                    active=True,
                    display_name='John Doe',
                    email='foo@bar',
                ),
            )
        ],
        edit_meta={
            'fields': {
                'summary': {
                    'required': True,
                    'schema': {'type': 'string', 'system': 'summary'},
                    'name': 'Summary',
                    'key': 'summary',
                    'operations': ['set'],
                }
            }
        },
        assignee=JiraUser(
            account_id='abe10be',
            active=True,
            display_name='Bart',
            email='bart@simpson.com',
        ),
        parent_issue_key='SCRUM-1',
        related_issues=[],
        comments=[
            IssueComment(
                id='1',
                author=JiraUser(
                    account_id='1',
                    active=True,
                    display_name='Bart Simpson',
                    email='bart@simpson.com',
                ),
                created=datetime(2025, 12, 30, 18, 0, 00),
                updated=datetime(2025, 12, 30, 18, 1, 00),
                update_author=JiraUser(
                    account_id='2',
                    active=True,
                    display_name='Lisa Simpson',
                    email='lisa@simpson.com',
                ),
                body='{"text": "hello world"}',
            )
        ],
        time_tracking=TimeTracking(
            original_estimate='2 minutes',
            remaining_estimate='1 minute',
            time_spent='1 minute',
            original_estimate_seconds=120,
            remaining_estimate_seconds=60,
            time_spent_seconds=60,
        ),
    )


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_related_work_items(config_for_testing):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    # WHEN
    related_items = build_related_work_items(work_item.get('fields').get('issuelinks'))
    # THEN
    assert related_items == [
        RelatedJiraIssue(
            id='10033',
            key='SCRUM-9',
            summary='(Sample) Add Login Rate Limiting',
            status=IssueStatus(
                name='In Progress',
                id='10001',
            ),
            issue_type=IssueType(id='10003', name='Task', scope_project=None),
            link_type='relates to',
            relation_type='outward',
            priority=IssuePriority(id='1', name='Highest'),
        ),
        RelatedJiraIssue(
            id='10075',
            key='SCRUM-1',
            summary='(Sample) Payment Processing with Async',
            status=IssueStatus(
                name='In Progress',
                id='10001',
            ),
            issue_type=IssueType(id='10001', name='Epic', scope_project=None),
            link_type='is cloned by',
            relation_type='inward',
            priority=IssuePriority(id='3', name='Medium'),
        ),
    ]


@patch('jiratui.api_controller.factories._build_related_inward_issue')
@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_related_work_items_fail_creating_inward_issue(
    configuration_mock: Mock,
    build_related_inward_issue_mock: Mock,
    config_for_testing,
):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    build_related_inward_issue_mock.side_effect = ValueError
    # WHEN
    related_items = build_related_work_items(work_item.get('fields').get('issuelinks'))
    # THEN
    assert related_items == [
        RelatedJiraIssue(
            id='10033',
            key='SCRUM-9',
            summary='(Sample) Add Login Rate Limiting',
            status=IssueStatus(
                name='In Progress',
                id='10001',
            ),
            issue_type=IssueType(id='10003', name='Task', scope_project=None),
            link_type='relates to',
            relation_type='outward',
            priority=IssuePriority(id='1', name='Highest'),
        )
    ]


@patch('jiratui.api_controller.factories._build_related_outward_issue')
@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_related_work_items_fail_creating_outward_issue(
    configuration_mock: Mock,
    build_related_outward_issue_mock: Mock,
    config_for_testing,
):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    build_related_outward_issue_mock.side_effect = ValueError
    # WHEN
    related_items = build_related_work_items(work_item.get('fields').get('issuelinks'))
    # THEN
    assert related_items == [
        RelatedJiraIssue(
            id='10075',
            key='SCRUM-1',
            summary='(Sample) Payment Processing with Async',
            status=IssueStatus(
                name='In Progress',
                id='10001',
            ),
            issue_type=IssueType(id='10001', name='Epic', scope_project=None),
            link_type='is cloned by',
            relation_type='inward',
            priority=IssuePriority(id='3', name='Medium'),
        ),
    ]
