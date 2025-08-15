from datetime import date

from jiratui.models import WorkItemsSearchOrderBy


def build_issue_search_jql(
    project_key: str | None = None,
    created_from: date | None = None,
    created_until: date | None = None,
    updated_from: date | None = None,
    updated_until: date | None = None,
    status: int | None = None,
    assignee: str | None = None,
    issue_type: int | None = None,
    jql_query: str | None = None,
    order_by: WorkItemsSearchOrderBy | None = None,
) -> str:
    """

    :param project_key:
    :param created_from:
    :param created_until:
    :param updated_from:
    :param updated_until:
    :param status: find work items whose status matches this status name/ID.
    :param assignee: find work items assigned to the given user. The user is specified by the account ID, email
    address or name of a user.
    :param issue_type:
    :param jql_query:
    :param order_by: used to specify the fields by whose values the search results will be sorted. This requirement
    needs to be placed at the end of the JQL query, otherwise the JQL will be invalid.
    :return:
    """
    fields: list[str] = []
    if project_key:
        fields.append(f'project = {project_key}')
    if created_from:
        value = date.strftime(created_from, '%Y-%m-%d')
        fields.append(f'created >= "{value}"')
    if created_until:
        value = date.strftime(created_until, '%Y-%m-%d')
        fields.append(f'created <= "{value}"')
    if updated_from:
        value = date.strftime(updated_from, '%Y-%m-%d')
        fields.append(f'updated >= "{value}"')
    if updated_until:
        value = date.strftime(updated_until, '%Y-%m-%d')
        fields.append(f'updated <= "{value}"')
    if status:
        fields.append(f'status = "{status}"')
    if assignee:
        fields.append(f'assignee = "{assignee}"')
    if issue_type:
        fields.append(f'type = {issue_type}')

    jql: str = ''
    if fields:
        jql = ' and '.join(fields)
    if jql_query:
        if jql:
            jql = f'{jql} and {jql_query}'
        else:
            jql = jql_query
    if 'order by' not in jql and order_by:
        if jql:
            jql = f'{jql} order by {order_by.value}'
        else:
            jql = f'order by {order_by.value}'
    return jql
