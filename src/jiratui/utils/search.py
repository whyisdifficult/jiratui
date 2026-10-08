from enum import Enum


class SearchFieldId(Enum):
    """The name/id of the fields used for retrieving data from work items when searching for work items from the API."""

    ID = 'id'
    KEY = 'key'
    STATUS = 'status'
    ISSUE_TYPE = 'issuetype'
    PARENT = 'parent'
    SUMMARY = 'summary'
    ASSIGNEE = 'assignee'
    REPORTER = 'reporter'


DEFAULT_WORK_ITEM_SEARCH_FIELDS = [
    SearchFieldId.ID.value,
    SearchFieldId.KEY.value,
    SearchFieldId.STATUS.value,
    SearchFieldId.ISSUE_TYPE.value,
    SearchFieldId.PARENT.value,
    SearchFieldId.SUMMARY.value,
]

SUPPORTED_USER_DEFINED_WORK_ITEM_SEARCH_FIELDS = {
    SearchFieldId.STATUS.value,
    SearchFieldId.ISSUE_TYPE.value,
    SearchFieldId.PARENT.value,
    SearchFieldId.ASSIGNEE.value,
    SearchFieldId.REPORTER.value,
    SearchFieldId.SUMMARY.value,
}

MAP_WORK_ITEM_SEARCH_FIELD_TO_SEARCH_RESULTS_COLUMNS = {
    SearchFieldId.ID.value: 'Id',
    SearchFieldId.KEY.value: 'Key',
    SearchFieldId.STATUS.value: 'Status',
    SearchFieldId.SUMMARY.value: 'Summary',
    SearchFieldId.ISSUE_TYPE.value: 'Type',
    SearchFieldId.PARENT.value: 'Parent',
    SearchFieldId.ASSIGNEE.value: 'Assignee',
    SearchFieldId.REPORTER.value: 'Reporter',
}


def get_work_item_search_fields(search_results_columns: list[str]) -> list[str]:
    """Retrieves the list of field ids extracted from work items when searching for work items.

    The field ids `id` and `key` are always returned because they are required for other operations in the application.

    Args:
        search_results_columns: an optional list of field ids as defined by the user via the configuration setting
        `config.search_results_columns`.

    Returns:
        If `search_results_columns` is empty then the default list of field ids is returned. Otherwise, it returns the
        fields ids in the list that are supported plus a work item's id and key field ids.
    """

    if not search_results_columns:
        return DEFAULT_WORK_ITEM_SEARCH_FIELDS
    user_defined_fields: list[str] = []
    for column in search_results_columns:
        if (
            column
            and (cleaned := column.strip())
            and cleaned.lower() in SUPPORTED_USER_DEFINED_WORK_ITEM_SEARCH_FIELDS
        ):
            user_defined_fields.append(cleaned)
    # we always need to ask for id and key; id and key are used for operations in the app
    return [SearchFieldId.ID.value, SearchFieldId.KEY.value] + user_defined_fields


def get_work_item_search_results_table_columns(search_results_columns: list[str]) -> list[str]:
    """Retrieves the list of column names to use for displaying the results of searching work items.

    Args:
        search_results_columns: an optional list of field ids as defined by the user via the configuration setting
        `config.search_results_columns`.

    Returns:
        If `search_results_columns` is empty then the default list of columns is returned. If the list is provided then
        the columns associated to the field ids on the list will be returned.
    """

    columns: list[str] = []
    if not search_results_columns:
        for field in DEFAULT_WORK_ITEM_SEARCH_FIELDS:
            if field != SearchFieldId.ID.value:
                columns.append(MAP_WORK_ITEM_SEARCH_FIELD_TO_SEARCH_RESULTS_COLUMNS.get(field, ''))
        return columns
    fields: list[str] = get_work_item_search_fields(search_results_columns)
    for field in fields:
        if field != SearchFieldId.ID.value:
            columns.append(MAP_WORK_ITEM_SEARCH_FIELD_TO_SEARCH_RESULTS_COLUMNS.get(field, ''))
    return columns
