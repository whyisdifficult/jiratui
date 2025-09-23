WORK_ITEM_STATUS_STYLES = {
    'done': 'green',
    'in review': 'dark_olive_green',
    'in progress': 'blue',
    'to do': 'yellow',
}

WORK_ITEM_TYPE_STYLES = {
    'bug': 'red',
    'epic': 'yellow',
    'task': 'blue',
}


def get_style_for_work_item_status(status_name: str) -> str:
    """Gets the style definition for displaying the status of a work item in the search results.

    Args:
        status_name:

    Returns:
        A color name or CSS-style definition; e.g. #FF0000 or 'red'
    """
    return WORK_ITEM_STATUS_STYLES.get(status_name, '') or ''


def get_style_for_work_item_type(status_name: str) -> str:
    """Gets the style definition for displaying the type of work item in the search results.

    Args:
        status_name: the name of the status.

    Returns:
        A color name or CSS-style definition; e.g. #FF0000 or 'red'
    """
    return WORK_ITEM_TYPE_STYLES.get(status_name, '') or ''
