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
