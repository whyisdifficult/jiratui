from jiratui.config import CONFIGURATION

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
    styling = CONFIGURATION.get().styling
    custom_colors = styling.work_item_status_colors if styling else None
    return (custom_colors or {}).get(status_name, WORK_ITEM_STATUS_STYLES.get(status_name, ''))


def get_style_for_work_item_type(type_name: str) -> str:
    """Gets the style definition for displaying the type of work item in the search results.

    Args:
        type_name: the name of the type.

    Returns:
        A color name or CSS-style definition; e.g. #FF0000 or 'red'
    """
    styling = CONFIGURATION.get().styling
    custom_colors = styling.work_item_type_colors if styling else None
    return (custom_colors or {}).get(type_name, WORK_ITEM_TYPE_STYLES.get(type_name, ''))
