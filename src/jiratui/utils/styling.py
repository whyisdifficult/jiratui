from jiratui.config import CONFIGURATION

WORK_ITEM_STATUS_STYLES = {
    'done': 'green',
    'in_review': 'dark_olive_green',
    'in_progress': 'blue',
    'to_do': 'yellow',
}

WORK_ITEM_TYPE_STYLES = {
    'bug': 'red',
    'epic': 'yellow',
    'task': 'blue',
}


def get_style_for_work_item_status(status_name: str) -> str:
    """Gets the style definition for displaying the status of a work item in the search results.

    ```{important}
    It assumes that the id/key of the status values defined in the config file's `styling` section are expressed in
    lowercase and w/o blank spaces.
    ```

    Args:
        status_name: the name of the status as defined by Jira.

    Returns:
        A color name or CSS-style definition; e.g. #FF0000 or 'red'
    """

    status_key = status_name.lower().replace(' ', '_')
    if (styling := CONFIGURATION.get().styling) and (
        custom_colors := styling.work_item_status_colors
    ):
        color = custom_colors.get(status_key, WORK_ITEM_STATUS_STYLES.get(status_key, ''))
        return color or WORK_ITEM_STATUS_STYLES.get(status_key, '')
    return WORK_ITEM_STATUS_STYLES.get(status_key, '')


def get_style_for_work_item_type(type_name: str) -> str:
    """Gets the style definition for displaying the type of work item in the search results.

    ```{important}
    It assumes that the id/key of the status values defined in the config file's `styling` section are expressed in
    lowercase and w/o blank spaces.
    ```

    Args:
        type_name: the name of the type.

    Returns:
        A color name or CSS-style definition; e.g. #FF0000 or 'red'
    """

    type_key = type_name.lower().replace(' ', '_')
    if (styling := CONFIGURATION.get().styling) and (
        custom_colors := styling.work_item_type_colors
    ):
        color = custom_colors.get(type_key, WORK_ITEM_TYPE_STYLES.get(type_key, ''))
        return color or WORK_ITEM_TYPE_STYLES.get(type_key, '')
    return WORK_ITEM_TYPE_STYLES.get(type_key, '')
