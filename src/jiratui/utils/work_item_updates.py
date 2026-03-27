from datetime import date

from jiratui.config import CONFIGURATION
from jiratui.models import CustomFieldTypes, IssuePriority, JiraIssueComponent, JiraUser


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


def work_item_due_date_has_changed(
    current_due_date: date | None = None, target_due_date: str | None = None
) -> bool:
    """Determines if the due date of a work item has changed wrt. to a new value selected by the user.

    Args:
        current_due_date: the current due date of the work item.
        target_due_date: the new due date set by the user.

    Returns:
        `True` id the due date has changed; `False` otherwise.
    """
    if current_due_date is None:
        if target_due_date:
            return True
        return False
    if not target_due_date:
        return True
    if str(current_due_date) == target_due_date:
        return False
    return True


def work_item_components_has_changed(
    current_components: list[JiraIssueComponent],
    target_components: list[dict],
) -> bool:
    """Determines if the components field of a work item has changed based on the current value and a new selection
    made by the user.

    Args:
        current_components: the list of components currently assigned to a work item.
        target_components: the new list of components.

    Returns:
        `True` if the list of components has changed.
    """

    if not current_components and target_components:
        return True
    if current_components and not target_components:
        return True
    if not current_components and not target_components:
        return False
    if len(current_components) != len(target_components):
        return True
    current_set = {x.id for x in current_components}
    if current_set.intersection({x.get('id') for x in target_components}) == current_set:
        return False
    return True


def updating_text_fields_is_supported() -> bool:
    """Determines whether the application supports editing rich/full text fields. These would include custom fields
    of type textarea or other system fields, e.g. environment.

    Jira Cloud Platform API v2 supports rich/full text fields; i.e. no ADF support; these fields are editable in
    JiraTUI.
    Jira Cloud Platform API v3 supports ADF; these fields are not editable in JiraTUI (yet).
    Jira Software Platform API v2 supports rich/full text fields; i.e. no ADF support; these fields are editable in
    JiraTUI.
    """

    # TODO add config variable to enable editing: config.enable_editing_rich_text_fields
    return (
        True  # CONFIGURATION.get().enable_editing_text_fields
        or not CONFIGURATION.get().cloud
        or (CONFIGURATION.get().cloud and CONFIGURATION.get().jira_api_version == 2)
    )


def field_supports_text_value(field_id: str, field_edit_metadata: dict) -> bool:
    """Determines if a Jira field supports rich/full text as value.

    Args:
        field_id: the ID of the field.
        field_edit_metadata: the field's edit metadata.

    Returns:
        `True` id the value of the field can be full-text (not simple strings); `False` otherwise.
    """

    schema = field_edit_metadata.get('schema', {})
    if field_id.startswith('customfield_') or field_edit_metadata.get('key', '').startswith(
        'customfield_'
    ):
        if schema.get('custom') == CustomFieldTypes.TEXTAREA.value:
            return True
        return False
    # TODO use enum for the list of field ids that support rich-text data, e.g. environment
    if schema.get('type') == 'string' and (
        (key := field_edit_metadata.get('key')) and key.lower() == 'environment'
    ):
        return True
    return False
