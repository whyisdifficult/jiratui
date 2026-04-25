from jiratui.models import IssuePriority, JiraUser


def work_item_priority_has_changed(
    current_priority: IssuePriority | None = None,
    target_priority: str | None = None,
) -> bool:
    """Determines if the priority of a work item has changed wrt. to a new priority selected by the user from the
    priority dropdown.

    Args:
        current_priority: the current priority of the work item.
        target_priority: the new priority selected by the user.

    Returns:
        `True` id the priority has changed; `False` otherwise.
    """

    if current_priority is None:
        if not target_priority:
            return False
        return True
    else:
        if not target_priority:
            return True
        if current_priority.id == target_priority:
            return False
        return True


def work_item_assignee_has_changed(
    current_assignee: JiraUser | None = None,
    target_assignee_account_id: str | None = None,
) -> bool:
    """Determines if the assignee of a work item has changed wrt. to a new assignee selected by the user from the
    assignee/users dropdown.

    Args:
        current_assignee: the work item's current assignee user.
        target_assignee_account_id: the account ID of the new user that we want to assign to the work item.

    Returns:
        `True` if the assignee of the work item has changed; `False` otherwise.
    """

    if current_assignee is None:
        if target_assignee_account_id is None:
            return False
        else:
            return True
    else:
        if target_assignee_account_id is None:
            return True
        else:
            return current_assignee.account_id != target_assignee_account_id


def work_item_reporter_has_changed(
    current_reporter: JiraUser | None = None,
    target_reporter_account_id: str | None = None,
) -> bool:
    """Determines if the assignee of a work item has changed wrt. to a new assignee selected by the user from the
    assignee/users dropdown.

    Args:
        current_reporter: the work item's current reporter user.
        target_reporter_account_id: the account ID of the new user that will act as the reporter of a work item.

    Returns:
        `True` if the reporter of the work item has changed; `False` otherwise.
    """

    if current_reporter is None:
        if target_reporter_account_id is None:
            return False
        else:
            return True
    else:
        if target_reporter_account_id is None:
            return True
        else:
            return current_reporter.account_id != target_reporter_account_id


def work_item_parent_has_changed(
    current_parent_key: str | None = None, target_parent_key: str | None = None
) -> bool:
    """Determines if the parent of a work item has changed wrt. to a new parent key selected by the user.

    Args:
        current_parent_key: the current parent of the work item.
        target_parent_key: the new parent key selected by the user.

    Returns:
        `True` id the priority has changed; `False` otherwise.
    """

    if current_parent_key is None:
        if not target_parent_key:
            return False
        return True
    if not target_parent_key:
        return True
    if current_parent_key == target_parent_key.strip():
        return False
    return True
