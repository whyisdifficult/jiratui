from src.models import IssuePriority, JiraUser


def can_update_work_item_priority(
    current_priority: IssuePriority | None = None,
    target_priority: str | None = None,
) -> bool:
    """Determines if we can/should update the priority of a work item based on the current and the new desired value.

    Args:
        current_priority: the work item's current priority.
        target_priority: the ID of the new priority that we want to assign to the work item.

    Returns:
        `True` if we should/can update the priority of the work item; `False` otherwise.
    """

    return (current_priority is None and target_priority) or (
        current_priority is not None and target_priority and target_priority != current_priority.id
    )


def can_update_work_item_assignee(
    current_assignee: JiraUser | None = None,
    target_assignee_account_id: str | None = None,
) -> bool:
    """Determines if we can/should update the assignee of a work item based on the current and the new desired value.

    Args:
        current_assignee: the work item's current assignee user.
        target_assignee_account_id: the account ID of the new user that we want to assign to the work item.

    Returns:
        `True` if we should/can update the assignee of the work item; `False` otherwise.
    """

    return (
        (
            target_assignee_account_id
            and current_assignee
            and target_assignee_account_id != current_assignee.account_id
        )
        or (target_assignee_account_id and not current_assignee)
        or (not target_assignee_account_id and current_assignee)
    )
