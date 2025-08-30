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
    return WORK_ITEM_STATUS_STYLES.get(status_name, '') or ''


def get_style_for_work_item_type(status_name: str) -> str:
    return WORK_ITEM_TYPE_STYLES.get(status_name, '') or ''
