import pytest

from jiratui.models import JiraUser
from jiratui.widgets.work_item_details.details import IssueDetailsWidget


@pytest.mark.parametrize(
    'users, current_assignee, default_assignable_users, expected_entries',
    [
        (
            [
                JiraUser(display_name='Bart', account_id='1', active=True),
                JiraUser(display_name='Lisa', account_id='2', active=True),
            ],
            JiraUser(display_name='Bart', account_id='1', active=True),
            [('Homer', '3')],
            [('Bart', '1'), ('Lisa', '2')],
        ),
        (
            [
                JiraUser(display_name='Bart', account_id='1', active=True),
                JiraUser(display_name='Lisa', account_id='2', active=True),
            ],
            JiraUser(display_name='Maggie', account_id='4', active=True),
            [('Homer', '3')],
            [('Bart', '1'), ('Lisa', '2'), ('Maggie', '4')],
        ),
        (
            [
                JiraUser(display_name='Bart', account_id='1', active=True),
                JiraUser(display_name='Lisa', account_id='2', active=True),
            ],
            None,
            [('Homer', '3')],
            [('Bart', '1'), ('Lisa', '2')],
        ),
        ([], None, [('Homer', '3')], [('Homer', '3')]),
        ([], None, [], []),
        (
            [],
            JiraUser(display_name='Maggie', account_id='4', active=True),
            [('Homer', '3')],
            [('Homer', '3'), ('Maggie', '4')],
        ),
        ([], JiraUser(display_name='Maggie', account_id='4', active=True), [], [('Maggie', '4')]),
        (
            [],
            JiraUser(display_name='Maggie', account_id='4', active=True),
            [('Maggie', '4')],
            [('Maggie', '4')],
        ),
    ],
)
def test_generate_assignable_users_for_dropdown(
    users: list[JiraUser] | None,
    current_assignee: JiraUser | None,
    default_assignable_users: list[tuple[str, str]] | None,
    expected_entries: list | None,
):
    # GIVEN
    widget = IssueDetailsWidget()
    # WHEN
    entries = widget._generate_assignable_users_for_dropdown(
        users, current_assignee, default_assignable_users
    )
    # THEN
    assert entries == expected_entries
