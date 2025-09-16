from datetime import date

import pytest

from jiratui.models import IssuePriority, JiraUser
from jiratui.utils.work_item_updates import (
    work_item_assignee_has_changed,
    work_item_due_date_has_changed,
    work_item_parent_has_changed,
    work_item_priority_has_changed,
)


@pytest.mark.parametrize(
    'current_priority, target_priority, expected_result',
    [
        (None, None, False),
        (None, '2', True),
        (IssuePriority(id='1', name='high'), None, True),
        (IssuePriority(id='1', name='high'), '', True),
        (IssuePriority(id='1', name='high'), '1', False),
        (IssuePriority(id='1', name='high'), '2', True),
    ],
)
def test_work_item_priority_has_changed(current_priority, target_priority, expected_result):
    assert work_item_priority_has_changed(current_priority, target_priority) is expected_result


@pytest.mark.parametrize(
    'current_assignee, target_assignee, expected_result',
    [
        (None, None, False),
        (None, '2', True),
        (JiraUser(account_id='1', display_name='Bart', active=True, email='foo@bar'), None, True),
        (JiraUser(account_id='1', display_name='Bart', active=True, email='foo@bar'), '1', False),
        (JiraUser(account_id='1', display_name='Bart', active=True, email='foo@bar'), '2', True),
    ],
)
def test_work_item_assignee_has_changed(current_assignee, target_assignee, expected_result):
    assert work_item_assignee_has_changed(current_assignee, target_assignee) is expected_result


@pytest.mark.parametrize(
    'current_parent_key, target_parent_key, expected_result',
    [
        (None, None, False),
        (None, '2', True),
        ('1', None, True),
        ('1', '1', False),
        ('1', '2', True),
    ],
)
def test_work_item_parent_has_changed(current_parent_key, target_parent_key, expected_result):
    assert work_item_parent_has_changed(current_parent_key, target_parent_key) is expected_result


@pytest.mark.parametrize(
    'current_due_date, target_due_date, expected_result',
    [
        (None, None, False),
        (None, '2025-06-10', True),
        (date(2025, 10, 10), None, True),
        (date(2025, 10, 10), '2025-10-10', False),
        (date(2025, 10, 9), '2025-06-10', True),
    ],
)
def test_work_item_due_date_has_changed(current_due_date, target_due_date, expected_result):
    assert work_item_due_date_has_changed(current_due_date, target_due_date) is expected_result
