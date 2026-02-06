from jiratui.config import CONFIGURATION

WORK_ITEM_STATUS_STYLES = {
    'done': 'green',
    'in_review': 'dark_olive_green',
    'in_progress': 'blue',
    'to_do': 'yellow',
}
"""The default colors to use to display/style the status of tasks, e.g. tasks listed in the search results tab."""

WORK_ITEM_TYPE_STYLES = {
    'bug': 'red',
    'epic': 'yellow',
    'task': 'blue',
}
"""The default colors to use to display/style the type of tasks, e.g. tasks listed in the search results tab."""

WORK_ITEM_PRIORITY_STYLES = {
    'lowest': 'grey',
    'low': 'yellow',
    'medium': 'purple',
    'high': 'orange',
    'highest': 'red',
}
"""The default colors to use to display/style the priority of tasks, e.g. tasks listed in the "related" tab."""


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

    if not status_name:
        return ''
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

    if not type_name:
        return ''
    type_key = type_name.lower().replace(' ', '_')
    if (styling := CONFIGURATION.get().styling) and (
        custom_colors := styling.work_item_type_colors
    ):
        color = custom_colors.get(type_key, WORK_ITEM_TYPE_STYLES.get(type_key, ''))
        return color or WORK_ITEM_TYPE_STYLES.get(type_key, '')
    return WORK_ITEM_TYPE_STYLES.get(type_key, '')


def get_style_for_work_item_priority(priority_name: str) -> str:
    """Gets the color style definition for displaying the priority of work item in the "related" tab.

    ```{important}
    It assumes that the id/key of the priority values defined in the config file's `styling` section are expressed in
    lowercase and w/o blank spaces.
    ```

    Args:
        priority_name: the name of the priority.

    Returns:
        A color name or CSS-style definition; e.g. #FF0000 or 'red'
    """

    if not priority_name:
        return ''
    priority_key = priority_name.lower().replace(' ', '_')
    if (styling := CONFIGURATION.get().styling) and (
        custom_colors := styling.work_item_priority_colors
    ):
        color = custom_colors.get(priority_key, WORK_ITEM_PRIORITY_STYLES.get(priority_key, ''))
        return color or WORK_ITEM_PRIORITY_STYLES.get(priority_key, '')
    return WORK_ITEM_PRIORITY_STYLES.get(priority_key, '')
