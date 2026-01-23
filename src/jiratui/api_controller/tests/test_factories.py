from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from jiratui.api_controller.factories import (
    WorkItemFactory,
    build_comments,
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
    JiraIssueComponent,
    JiraUser,
    Project,
    RelatedJiraIssue,
    TimeTracking,
)
from jiratui.utils.test_utilities import load_json_response


@pytest.fixture
def config_for_testing() -> ApplicationConfiguration:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        active_sprint_on_startup=False,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='ERROR',
        search_issues_default_day_interval=15,
    )
    return config_mock


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
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world 1'}]}
                ],
            },
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
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world'}]}
                ],
            },
        },
    ]


@pytest.fixture
def raw_comments_without_adf() -> list[dict]:
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
            'body': {'type': 'doc', 'version': 1, 'content': 'hello world 1'},
        }
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
            body={
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world 1'}]}
                ],
            },
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
            body={
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world'}]}
                ],
            },
        ),
    ]


def test_build_comments_no_adf(raw_comments_without_adf):
    # WHEN
    comments = build_comments(raw_comments_without_adf)
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
            body={'type': 'doc', 'version': 1, 'content': 'hello world 1'},
        )
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
            body={
                'type': 'doc',
                'version': 1,
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world'}]}
                ],
            },
        ),
    ]


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_issue_instance(configuration_mock: Mock, config_for_testing):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    # WHEN
    issue = WorkItemFactory.create_work_item(work_item)
    # THEN
    assert isinstance(issue, JiraIssue)
    assert issue.id == '10002'
    assert issue.key == 'SCRUM-10'
    assert issue.summary == '(Sample) Set Up Payment Logging'
    assert issue.status == IssueStatus(
        name='In Progress',
        id='10001',
    )
    assert issue.project == Project(id='10000', name='Test Project', key='SCRUM')
    assert issue.created == datetime(2025, 7, 5, 14, 34, 59)
    assert issue.updated == datetime(2025, 7, 14, 22, 33, 38)
    assert issue.due_date == datetime(2025, 12, 31).date()
    assert issue.reporter == JiraUser(
        account_id='abe10be',
        active=True,
        display_name='Bart',
        email='bart@simpson.com',
    )
    assert issue.issue_type == IssueType(
        id='10003', name='Task', scope_project=None, hierarchy_level=0
    )
    assert issue.description == {
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
    }
    assert issue.attachments == [
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
    ]
    assert issue.time_tracking == TimeTracking(
        original_estimate='2 minutes',
        remaining_estimate='1 minute',
        time_spent='1 minute',
        original_estimate_seconds=120,
        remaining_estimate_seconds=60,
        time_spent_seconds=60,
    )


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_issue_instance_with_more_details(configuration_mock: Mock, config_for_testing):
    # GIVEN
    work_item = load_json_response(__file__, 'issue.json')
    # WHEN
    issue = WorkItemFactory.create_work_item(work_item)
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
        issue_type=IssueType(id='10003', name='Task', scope_project=None, hierarchy_level=0),
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
        related_issues=[
            RelatedJiraIssue(
                id='10033',
                key='SCRUM-9',
                summary='(Sample) Add Login Rate Limiting',
                status=IssueStatus(
                    id='10001',
                    name='In Progress',
                    description=None,
                ),
                issue_type=IssueType(
                    id='10003',
                    name='Task',
                    hierarchy_level=None,
                    scope_project=None,
                ),
                link_type='relates to',
                relation_type='outward',
                priority=IssuePriority(
                    id='1',
                    name='Highest',
                ),
            ),
            RelatedJiraIssue(
                id='10075',
                key='SCRUM-1',
                summary='(Sample) Payment Processing with Async',
                status=IssueStatus(
                    id='10001',
                    name='In Progress',
                    description=None,
                ),
                issue_type=IssueType(
                    id='10001',
                    name='Epic',
                    hierarchy_level=None,
                    scope_project=None,
                ),
                link_type='is cloned by',
                relation_type='inward',
                priority=IssuePriority(
                    id='3',
                    name='Medium',
                ),
            ),
        ],
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
                body={
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world'}]}
                    ],
                },
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
        components=[],
        additional_fields={
            'aggregateprogress': {
                'progress': 0,
                'total': 0,
            },
            'aggregatetimeestimate': None,
            'aggregatetimeoriginalestimate': None,
            'aggregatetimespent': None,
            'creator': {
                'accountId': 'abe10be',
                'accountType': 'atlassian',
                'active': True,
                'displayName': 'Bart',
                'emailAddress': 'bart@simpson.com',
                'timeZone': 'Europe/Amsterdam',
            },
            'environment': None,
            'fixVersions': [],
            'issuerestriction': {
                'issuerestrictions': {},
                'shouldDisplay': True,
            },
            'lastViewed': '2025-07-09T11:34:16',
            'progress': {
                'progress': 0,
                'total': 0,
            },
            'security': None,
            'statusCategory': {
                'colorName': 'yellow',
                'id': 4,
                'key': 'indeterminate',
                'name': 'In Progress',
            },
            'statuscategorychangedate': '2025-07-08T15:23:50.516+0200',
            'subtasks': [],
            'timeestimate': None,
            'timeoriginalestimate': None,
            'timespent': None,
            'versions': [],
            'votes': {
                'hasVoted': False,
                'votes': 0,
            },
            'watches': {
                'isWatching': True,
                'watchCount': 1,
            },
            'worklog': {
                'maxResults': 20,
                'startAt': 0,
                'total': 0,
                'worklogs': [],
            },
            'workratio': -1,
        },
        custom_fields={
            'customfield_10001': None,
            'customfield_10015': None,
            'customfield_10016': None,
            'customfield_10019': '0|i0001r:',
            'customfield_10020': [
                {
                    'boardId': 1,
                    'endDate': '2025-07-19T12:35:00.967Z',
                    'id': 2,
                    'name': 'SCRUM Sprint 0',
                    'startDate': '2025-07-05T12:35:00.967Z',
                    'state': 'active',
                },
            ],
            'customfield_10021': None,
            'customfield_10036': None,
        },
    )


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_issue_instance_with_more_details_no_adf(
    configuration_mock: Mock, config_for_testing
):
    # comments and description do not use ADF
    # GIVEN
    work_item = load_json_response(__file__, 'issue_no_adf.json')
    # WHEN
    issue = WorkItemFactory.create_work_item(work_item)
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
        issue_type=IssueType(id='10003', name='Task', scope_project=None, hierarchy_level=0),
        description='Create a logging system to store payment transaction metadata.',
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
        related_issues=[
            RelatedJiraIssue(
                id='10033',
                key='SCRUM-9',
                summary='(Sample) Add Login Rate Limiting',
                status=IssueStatus(
                    id='10001',
                    name='In Progress',
                    description=None,
                ),
                issue_type=IssueType(
                    id='10003',
                    name='Task',
                    hierarchy_level=None,
                    scope_project=None,
                ),
                link_type='relates to',
                relation_type='outward',
                priority=IssuePriority(
                    id='1',
                    name='Highest',
                ),
            ),
            RelatedJiraIssue(
                id='10075',
                key='SCRUM-1',
                summary='(Sample) Payment Processing with Async',
                status=IssueStatus(
                    id='10001',
                    name='In Progress',
                    description=None,
                ),
                issue_type=IssueType(
                    id='10001',
                    name='Epic',
                    hierarchy_level=None,
                    scope_project=None,
                ),
                link_type='is cloned by',
                relation_type='inward',
                priority=IssuePriority(
                    id='3',
                    name='Medium',
                ),
            ),
        ],
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
                body={'type': 'doc', 'version': 1, 'content': 'hello world 1'},
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
        components=[],
        additional_fields={
            'aggregateprogress': {
                'progress': 0,
                'total': 0,
            },
            'aggregatetimeestimate': None,
            'aggregatetimeoriginalestimate': None,
            'aggregatetimespent': None,
            'creator': {
                'accountId': 'abe10be',
                'accountType': 'atlassian',
                'active': True,
                'displayName': 'Bart',
                'emailAddress': 'bart@simpson.com',
                'timeZone': 'Europe/Amsterdam',
            },
            'environment': None,
            'fixVersions': [],
            'issuerestriction': {
                'issuerestrictions': {},
                'shouldDisplay': True,
            },
            'lastViewed': '2025-07-09T11:34:16',
            'progress': {
                'progress': 0,
                'total': 0,
            },
            'security': None,
            'statusCategory': {
                'colorName': 'yellow',
                'id': 4,
                'key': 'indeterminate',
                'name': 'In Progress',
            },
            'statuscategorychangedate': '2025-07-08T15:23:50.516+0200',
            'subtasks': [],
            'timeestimate': None,
            'timeoriginalestimate': None,
            'timespent': None,
            'versions': [],
            'votes': {
                'hasVoted': False,
                'votes': 0,
            },
            'watches': {
                'isWatching': True,
                'watchCount': 1,
            },
            'worklog': {
                'maxResults': 20,
                'startAt': 0,
                'total': 0,
                'worklogs': [],
            },
            'workratio': -1,
        },
        custom_fields={
            'customfield_10001': None,
            'customfield_10015': None,
            'customfield_10016': None,
            'customfield_10019': '0|i0001r:',
            'customfield_10020': [
                {
                    'boardId': 1,
                    'endDate': '2025-07-19T12:35:00.967Z',
                    'id': 2,
                    'name': 'SCRUM Sprint 0',
                    'startDate': '2025-07-05T12:35:00.967Z',
                    'state': 'active',
                },
            ],
            'customfield_10021': None,
            'customfield_10036': None,
        },
    )
    assert issue.get_custom_fields() == {
        'customfield_10001': None,
        'customfield_10015': None,
        'customfield_10016': None,
        'customfield_10019': '0|i0001r:',
        'customfield_10020': [
            {
                'boardId': 1,
                'endDate': '2025-07-19T12:35:00.967Z',
                'id': 2,
                'name': 'SCRUM Sprint 0',
                'startDate': '2025-07-05T12:35:00.967Z',
                'state': 'active',
            },
        ],
        'customfield_10021': None,
        'customfield_10036': None,
    }
    assert issue.get_additional_fields() == {
        'aggregateprogress': {
            'progress': 0,
            'total': 0,
        },
        'aggregatetimeestimate': None,
        'aggregatetimeoriginalestimate': None,
        'aggregatetimespent': None,
        'creator': {
            'accountId': 'abe10be',
            'accountType': 'atlassian',
            'active': True,
            'displayName': 'Bart',
            'emailAddress': 'bart@simpson.com',
            'timeZone': 'Europe/Amsterdam',
        },
        'environment': None,
        'fixVersions': [],
        'issuerestriction': {
            'issuerestrictions': {},
            'shouldDisplay': True,
        },
        'lastViewed': '2025-07-09T11:34:16',
        'progress': {
            'progress': 0,
            'total': 0,
        },
        'security': None,
        'statusCategory': {
            'colorName': 'yellow',
            'id': 4,
            'key': 'indeterminate',
            'name': 'In Progress',
        },
        'statuscategorychangedate': '2025-07-08T15:23:50.516+0200',
        'subtasks': [],
        'timeestimate': None,
        'timeoriginalestimate': None,
        'timespent': None,
        'versions': [],
        'votes': {
            'hasVoted': False,
            'votes': 0,
        },
        'watches': {
            'isWatching': True,
            'watchCount': 1,
        },
        'worklog': {
            'maxResults': 20,
            'startAt': 0,
            'total': 0,
            'worklogs': [],
        },
        'workratio': -1,
    }


@patch('jiratui.api_controller.factories.CONFIGURATION')
def test_build_issue_instance_with_components(configuration_mock: Mock, config_for_testing):
    # GIVEN
    json_data = load_json_response(__file__, 'issue.json')
    json_data['fields']['components'] = [{'id': '1', 'name': 'Component 1'}]
    work_item = json_data
    # WHEN
    issue = WorkItemFactory.create_work_item(work_item)
    # THEN
    assert isinstance(issue, JiraIssue)
    assert issue.components == [JiraIssueComponent(id='1', name='Component 1')]


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
