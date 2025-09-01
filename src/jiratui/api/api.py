from datetime import date
import json
from typing import Any

import httpx

from jiratui.api.client import AsyncJiraClient, JiraClient
from jiratui.api.utils import build_issue_search_jql
from jiratui.constants import ISSUE_SEARCH_DEFAULT_MAX_RESULTS
from jiratui.models import WorkItemsSearchOrderBy


class JiraAPI:
    """Implements methods to connect to the Jira REST API.

    Supported version: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#version
    """

    API_PATH_PREFIX = '/rest/api/3/'

    def __init__(self, base_url: str, api_username: str, api_token: str):
        self.authentication = httpx.BasicAuth(api_username, api_token)
        self.client = AsyncJiraClient(
            base_url=f'{base_url.rstrip("/")}{self.API_PATH_PREFIX}',
            api_username=api_username,
            api_token=api_token,
        )
        self.sync_client = JiraClient(
            base_url=f'{base_url.rstrip("/")}{self.API_PATH_PREFIX}',
            api_username=api_username,
            api_token=api_token,
        )
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        return self._base_url

    async def search_projects(
        self,
        offset: int | None = None,
        limit: int | None = None,
        query: str | None = None,
        order_by: str | None = None,
        keys: list[str] = None,
    ) -> dict:
        """Retrieves a paginated list of projects visible to the user (making the request).

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get

        Args:
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. Must be less than or equal to 100.
            query: filter the results using a literal string. Projects with a matching key or name are returned
            (case-insensitive).
            order_by: sort the results by a field: `key` (default), `category`, `issueCount`, `lastIssueUpdatedTime`,
            `name`, `owner`, `archivedDate`, `deletedDate`.
            keys: the project keys to filter the results by.

        Returns:
            A dictionary with the details of the projects.
        """
        params: dict[str, Any] = {}
        if order_by:
            params['orderBy'] = order_by
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        if query is not None:
            params['query'] = query
        if keys:
            params['keys'] = ','.join(keys[:50])

        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='project/search', params=params
        )

    async def get_project_statuses(self, project_key: str) -> list[dict]:
        """Retrieves the valid statuses for a project.

        The statuses are grouped by issue type, as each project has a set of valid issue types and each issue type has
        a set of valid statuses.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-projectidorkey-statuses-get

        Args:
            project_key: the (case-sensitive) project ID or project key.

        Returns:
            A list of dictionaries.
        """
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url=f'project/{project_key}/statuses'
        )

    async def get_issue_types_for_user(self) -> list[dict]:
        """Retrieves all the issue types.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/#api-rest-api-3-issuetype-get

        Returns:
            A list of dictionaries with the details of the types of issues.
        """
        return await self.client.make_request(method=httpx.AsyncClient.get, url='issuetype')  # type:ignore[return-value]

    async def get_statuses(
        self,
        project_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Retrieves a paginated list of statuses that match a search on project.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-status/#api-rest-api-3-statuses-search-get

        Args:
            project_id: the ID of the project the status is part of or null for global statuses.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. The Default is 200.

        Returns:
            A dictionary with the statuses.
        """
        params: dict[str, Any] = {}
        if project_id:
            params['projectId'] = project_id
        if offset:
            params['startAt'] = offset
        if limit:
            params['maxResults'] = limit
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='statuses/search', params=params
        )

    async def status(self) -> list[dict]:
        return await self.client.make_request(method=httpx.AsyncClient.get, url='status')  # type:ignore[return-value]

    async def get_project(self, key: str) -> dict:
        """Retrieves the details of a project.

        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-projectidorkey-get

        Args:
            key: the project ID or project key (case-sensitive).

        Returns:
            A dictionary with the details of the project.
        """
        return await self.client.make_request(method=httpx.AsyncClient.get, url=f'project/{key}')  # type:ignore[return-value]

    async def user_assignable_search(
        self,
        project_id_or_key: str | None = None,
        issue_key: str | None = None,
        issue_id: str | None = None,
        offset: int | None = None,
        limit: int | None = 50,
        query: str | None = None,
    ) -> list[dict]:
        """Retrieves a list of users that can be assigned to an issue.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-assignable-search-get

        Args:
            project_id_or_key: the project ID or project key (case-sensitive). Required, unless `issue_key` or
            `issue_id` is specified.
            issue_key: the key of the issue. Required, unless issueId or project is specified.
            issue_id: the ID of the issue. Required, unless issueKey or project is specified.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return. Default is `50`.
            query: a string that is matched against user attributes, such as `displayName`, and `emailAddress`, to find
            relevant users. The string can match the prefix of the attribute's value. For example, `query=john` matches
            a user with a `displayName` of John Smith and a user with an `emailAddress` of johnson@example.com.
            Required, unless `username` or `accountId` is specified.

        Returns:
            A list of dictionaries with the details of the users.
        """
        if not any([project_id_or_key, issue_id, issue_key]):
            raise ValueError('One of these parameters is required: project_id, issue_id, issue_key')

        params: dict[str, Any] = {}
        if project_id_or_key:
            params['project'] = project_id_or_key  # accept case-sensitive project key as well
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        if query:
            params['query'] = query
        if issue_key:
            params['issueKey'] = issue_key
        if issue_id:
            params['issueId'] = issue_id

        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='user/assignable/search', params=params
        )

    async def user_assignable_multi_projects(
        self,
        project_keys: list[str] = None,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Retrieves the users who can be assigned issues in one or more projects.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-assignable-multiprojectsearch-get

        Args:
            project_keys: a list of project keys (case-sensitive). This parameter accepts a comma-separated list.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. Default is `50`.
            query: a string that is matched against user attributes, such as `displayName`, and `emailAddress`, to find
            relevant users. The string can match the prefix of the attribute's value. For example, `query=john` matches
            a user with a `displayName` of John Smith and a user with an `emailAddress` of johnson@example.com.
            Required, unless `username` or `accountId` is specified.

        Returns:
            A list of dictionaries with the details of the users.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        if project_keys:
            params['projectKeys'] = ','.join(project_keys)
        if query:
            params['query'] = query
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url='user/assignable/multiProjectSearch',
            params=params,
        )

    async def get_issue(
        self,
        issue_id_or_key: str,
        fields: str | None = None,
        properties: str | None = None,
    ) -> dict:
        """Retrieves the details of a work item by ID or key.

        The issue is identified by its ID or key, however, if the identifier doesn't match an issue, a case-insensitive
        search and check for moved issues is performed. If a matching issue is found its details are returned, a 302
        or other redirect is not returned. The issue key returned in the response is the key of the issue found.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get

        Args:
            issue_id_or_key: the ID or case-sensitive key of the work item to retrieve.
            fields: a list of fields to return for the issue. This parameter accepts a comma-separated list. Use it
            to retrieve a subset of fields. Allowed values:
                *all Returns all fields.
                *navigable Returns navigable fields.
            Any issue field, prefixed with a minus to exclude.
            properties: a list of issue properties to return for the issue. This parameter accepts a comma-separated
            list. Allowed values:
                *all Returns all issue properties.
                Any issue property key, prefixed with a minus to exclude.

        Returns:
            A dictionary with the detail sof the issue.
        """
        params: dict[str, Any] = {'expand': 'editmeta'}
        if fields is not None:
            params['fields'] = fields
        if properties is not None:
            params['properties'] = properties
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/{issue_id_or_key}',
            params=params,
        )

    async def get_issue_remote_links(
        self, issue_id_or_key: str, global_id: str | None = None
    ) -> list[dict]:
        """Retrieves the remote issue links for an issue.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get

        Args:
            issue_id_or_key: the key or ID of the issue whose remote links we want to retrieve.
            global_id: the global ID of the remote issue link.

        Returns:
            A list of dictionaries.
        """
        params: dict[str, str] = {}
        if global_id:
            params['globalId'] = global_id
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/{issue_id_or_key}/remotelink',
            params=params,
        )

    async def create_issue_remote_link(self, issue_id_or_key: str, url: str, title: str) -> None:
        """Creates or updates a remote issue link for an issue.

        See Also:
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-post

        Args:
            issue_id_or_key: the ID or case-sensitive key of the work item
            url: the URL of the link.
            title: the title of the link.

        Returns:
            Nothing.
        """
        payload: dict[str, Any] = {
            'object': {
                'title': title,
                'url': url,
            }
        }
        await self.client.make_request(
            method=httpx.AsyncClient.post,
            url=f'issue/{issue_id_or_key}/remotelink',
            data=json.dumps(payload),
        )

    async def delete_issue_remote_link(self, issue_id_or_key: str, link_id: str) -> None:
        """Deletes a web link associated to a work item.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-linkid-delete

        Args:
            issue_id_or_key: the ID or case-sensitive key of the work item
            link_id: the IF of the link.

        Returns:
            Nothing.
        """
        await self.client.make_request(
            method=httpx.AsyncClient.delete,
            url=f'issue/{issue_id_or_key}/remotelink/{link_id}',
        )
        return None

    async def search_issues(
        self,
        project_key: str | None = None,
        created_from: date | None = None,
        created_until: date | None = None,
        updated_from: date | None = None,
        updated_until: date | None = None,
        status: int | None = None,
        assignee: str | None = None,
        issue_type: int | None = None,
        jql_query: str | None = None,
        search_in_active_sprint: bool = False,
        fields: list[str] | None = None,
        next_page_token: str | None = None,
        limit: int | None = None,
        order_by: WorkItemsSearchOrderBy | None = None,
    ) -> dict:
        """Searches for issues using JQL. Recent updates might not be immediately visible in the returned search
        results.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-post

        Args:
            project_key: search items that belong to the project with this (case-sensitive) key.
            created_from: search items created from this date forward.
            created_until: search items created until this date.
            updated_from: search items updated from this date forward.
            updated_until: search items updated until this date
            status: search items with this status id.
            assignee: search items assigned to this user (by account id).
            issue_type: search items with this type id.
            jql_query: a JQL expression to filter items.
            search_in_active_sprint: if `True` only work items that belong to the currently active sprint will be
            retrieved.
            fields: retrieve these fields for every item found.
            next_page_token: an optional token to retrieve the next page of results.
            limit: retrieve this max number of results per page.
            order_by: sort the items according to these criteria. This requirement needs to be placed at the end of
            the JQL query, otherwise the JQL will be invalid. Possible values are:
            - order by created asc
            - order by created desc
            - order by priority asc
            - order by priority desc
            - order by key asc
            - order by key desc

        Returns:
            A dictionary with the results.
        """
        jql: str = build_issue_search_jql(
            project_key=project_key,
            created_from=created_from,
            created_until=created_until,
            updated_from=updated_from,
            updated_until=updated_until,
            status=status,
            assignee=assignee,
            issue_type=issue_type,
            jql_query=jql_query,
            search_in_active_sprint=search_in_active_sprint,
            order_by=order_by,
        )
        payload: dict[str, Any] = {
            'jql': jql,
            'maxResults': limit or ISSUE_SEARCH_DEFAULT_MAX_RESULTS,
        }
        if fields:
            payload['fields'] = fields
        if next_page_token:
            payload['nextPageToken'] = next_page_token
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post, url='search/jql', data=json.dumps(payload)
        )

    async def work_items_search_approximate_count(
        self,
        project_key: str | None = None,
        created_from: date | None = None,
        created_until: date | None = None,
        updated_from: date | None = None,
        status: int | None = None,
        assignee: str | None = None,
        issue_type: int | None = None,
        jql_query: str | None = None,
    ) -> dict:
        """Provides an estimated count of the issues that match the JQL. Recent updates might not be immediately visible
        in the returned output. This endpoint requires JQL to be bounded.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-approximate-count-post

        Args:
            project_key: search items that belong to the project with this (case-sensitive) key.
            created_from: search items created from this date forward.
            created_until: search items created until this date.
            updated_from: search items updated from this date forward.
            status: search items with this status id.
            assignee: search items assigned to this user (by account id).
            issue_type: search items with this type id.
            jql_query: a JQL expression to filter items.

        Returns:
            A dictionary with the estimated number of items that match the search criteria.
        """
        jql: str = build_issue_search_jql(
            project_key=project_key,
            created_from=created_from,
            created_until=created_until,
            updated_from=updated_from,
            status=status,
            assignee=assignee,
            issue_type=issue_type,
            jql_query=jql_query,
        )

        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url='search/approximate-count',
            data=json.dumps({'jql': jql}),
        )

    async def evaluate_expression(
        self, expression: str, issue_key: str = None, project_key: str = None
    ) -> dict:
        """Evaluates a JQL expression.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-expressions/#api-rest-api-3-expression-evaluate-post

        Args:
            expression: a JQL expression.
            issue_key: a case-sensitive work item key.
            project_key: a case-sensitive project key.

        Returns:
            A dictionary with the result of the evaluation.
        """
        payload: dict[str, Any] = {'expression': expression}
        if issue_key:
            payload['issue'] = {'key': issue_key}
        if project_key:
            payload['project'] = {'key': project_key}
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url='expression/evaluate',
            data=json.dumps(payload),
        )

    async def server_info(self) -> dict:
        """Retrieves information of the Jira server.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-server-info/#api-group-server-info

        Returns:
            A dictionary with the details.
        """
        return await self.client.make_request(method=httpx.AsyncClient.get, url='serverInfo')  # type:ignore[return-value]

    async def myself(self) -> dict:
        """Retrieves information of the Jira user connecting to the Jira server.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-myself/#api-rest-api-3-myself-get

        Returns:
            A dictionary with the details.
        """
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url='myself',
            params={'expand': 'groups,applicationRoles'},
        )

    async def search_users(self, offset: int | None = None, limit: int | None = None) -> list[dict]:
        """Retrieves a list of all users, including active users, inactive users and previously deleted users that have
        an Atlassian account.

        See Also:
           https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-users-search-get

        Args:
            offset: the index of the first item to return.
            limit: the maximum number of items to return (limited to 1000).

        Returns:
            A list of dictionaries with the details of the users.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='users/search', params=params
        )

    async def user_search(
        self,
        username: str | None = None,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Retrieves a list of active users that match the search string and property.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-search-get

        Args:
            username: the username to filter users.
            query: a query string that is matched against user attributes (`displayName`, and `emailAddress`) to
            find relevant users.
            offset: the index of the first item to return.
            limit: the maximum number of items to return (limited to 1000).

        Returns:
            A list of dictionaries with the details of the users.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        if username is not None:
            params['username'] = username
        if query is not None:
            params['query'] = query
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='user/search', params=params
        )

    async def get_groups_in_bulk(
        self,
        offset: int | None = None,
        limit: int | None = None,
        groups_ids: list[str] | None = None,
        groups_names: list[str] | None = None,
    ) -> dict:
        """Retrieves a paginated list of groups.

        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-bulk-get

        Args:
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. The default is 50.
            groups_ids: a list of groups IDs to retrieve.
            groups_names: a list of groups names to retrieve.

        Returns:
            A dictionary with the results of the current page.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params['maxResults'] = limit
        if offset is not None:
            params['startAt'] = offset
        if groups_ids:
            params['groupId'] = ','.join(groups_ids)
        if groups_names:
            params['groupName'] = ','.join(groups_names)
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='group/bulk', params=params
        )

    async def get_users_in_group(
        self, group_id: str, offset: int | None = None, limit: int | None = None
    ) -> dict:
        """Retrieves a paginated list of all (active) users in a group.

        Note that users are ordered by username, however the username is not returned in the results due to privacy
        reasons.

        See Also:
            - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-member-get
            - https://support.atlassian.com/user-management/docs/default-groups-and-permissions/

        Args:
            group_id: The ID of the group.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page (number should be between 1 and 50).

        Returns:
            A dictionary with the details of the users.
        """
        params: dict[str, Any] = {
            'includeInactiveUsers': False,
        }
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        if group_id:
            params['groupId'] = group_id
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='group/member', params=params
        )

    async def add_comment(self, issue_id_or_key: str, message: str) -> dict:
        """Adds a comment to an issue.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post

        Args:
            issue_id_or_key: the case-sensitive key of the work item whose comment we want to retrieve.
            message: the message of the comment.

        Returns:
            A dictionary with the details of the comment.
        """
        payload = {
            'body': {
                'content': [{'content': [{'text': message, 'type': 'text'}], 'type': 'paragraph'}],
                'type': 'doc',
                'version': 1,
            }
        }
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url=f'issue/{issue_id_or_key}/comment',
            data=json.dumps(payload),
        )

    async def get_comment(self, issue_id_or_key: str, comment_id: str) -> dict:
        """Retrieves the detail sof a comment.

        See Also:
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-id-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item whose comment we want to retrieve.
            comment_id: the ID of the comment.

        Returns:
            A dictionary with the details of the comment.
        """
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/{issue_id_or_key}/comment/{comment_id}',
        )

    async def get_comments(
        self, issue_id_or_key: str, offset: int | None = None, limit: int | None = None
    ) -> dict:
        """Retrieves the comments of a work item.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item whose comment we want to retrieve.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. The default is 50.

        Returns:
            A dictionary with the details of the comments.
        """
        params: dict[str, Any] = {'orderBy': '-created'}
        if limit is not None:
            params['maxResults'] = limit
        if offset is not None:
            params['startAt'] = offset
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/{issue_id_or_key}/comment',
            params=params,
        )

    async def delete_comment(self, issue_id_or_key: str, comment_id: str) -> None:
        """Deletes a comment.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-id-delete

        Args:
            issue_id_or_key: the case-sensitive key of the work item whose comment we want to delete.
            comment_id: the ID of the comment.

        Returns:
            Nothing if the comment is deleted; an exception otherwise.
        """
        await self.client.make_request(
            method=httpx.AsyncClient.delete,
            url=f'issue/{issue_id_or_key}/comment/{comment_id}',
        )
        return None

    async def issue_edit_metadata(self, issue_id_or_key: str) -> dict:
        """Retrieves the edit screen fields for an issue that are visible to and editable by the user.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-editmeta-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item.

        Returns:
            A dictionary with the metadata.
        """
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url=f'issue/{issue_id_or_key}/editmeta'
        )

    async def update_issue(self, issue_id_or_key: str, payload: dict) -> dict:
        """Updates a work item.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-put

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            payload: the fields and their values.

        Returns:
            A dictionary with the details of the work item after the update.
        """
        data = {'update': payload}
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.put,
            url=f'issue/{issue_id_or_key}',
            data=json.dumps(data),
            params={'returnIssue': True},
        )

    async def create_work_item(self, fields: dict) -> dict:
        """Creates a work item.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post

        Args:
            fields: a dictionary with the fields and their values to create the item.

        Returns:
            A dictionary with the details of the new item.
        """
        payload = {'fields': fields}
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post, url='issue', data=json.dumps(payload)
        )

    async def transitions(self, issue_id_or_key: str) -> dict:
        """Retrieves the applicable transitions for a work item.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item.

        Returns:
            A dictionary with the details of the transitions.
        """
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url=f'issue/{issue_id_or_key}/transitions'
        )

    async def transition_issue(self, issue_id_or_key: str, transition_id: str) -> None:
        """Performs an issue transition.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-post

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            transition_id: the ID of the status transition.

        Returns:
            Nothing.
        """
        payload = {'transition': transition_id}
        await self.client.make_request(
            method=httpx.AsyncClient.post,
            url=f'issue/{issue_id_or_key}/transitions',
            data=json.dumps(payload),
        )
        return None

    async def create_issue_link(
        self,
        left_issue_key: str,
        right_issue_key: str,
        link_type: str,
        link_type_id: str,
    ) -> None:
        """Creates a link between two issues. Use this operation to indicate a relationship between two issues and
        optionally add a comment to the "from" (outward) issue

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-links/#api-rest-api-3-issuelink-post

        Args:
            left_issue_key: the case-sensitive key of the work item.
            right_issue_key: the case-sensitive key of the work item.
            link_type: the type of link.
            link_type_id: the ID of the type of link.

        Returns:
            Nothing.
        """
        payload = {
            'type': {
                'id': link_type_id,
            },
        }
        if link_type == 'inward':
            payload['inwardIssue'] = {'key': right_issue_key}
            payload['outwardIssue'] = {'key': left_issue_key}
        else:
            payload['inwardIssue'] = {'key': left_issue_key}
            payload['outwardIssue'] = {'key': right_issue_key}
        await self.client.make_request(
            method=httpx.AsyncClient.post,
            url='issueLink',
            data=json.dumps(payload),
        )
        return None

    async def issue_link_types(self) -> dict:
        """Retrieves a list of all issue link types.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/#api-rest-api-3-issuelinktype-get

        Returns:
            A dictionary with the types of links between work items.
        """
        return await self.client.make_request(method=httpx.AsyncClient.get, url='issueLinkType')  # type:ignore[return-value]

    async def delete_issue_link(self, link_id: str) -> None:
        await self.client.make_request(method=httpx.AsyncClient.delete, url=f'issueLink/{link_id}')
        return None

    async def get_issue_create_meta(
        self, project_id_or_key: str, issue_type_id: str, offset: int = 0, limit: int | None = None
    ) -> dict:
        """Retrieves a page of field metadata for a specified project and type of issue id.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-createmeta-projectidorkey-issuetypes-issuetypeid-get

        Args:
            project_id_or_key: the case-sensitive key of the project.
            issue_type_id: the ID of a type of issue.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page.

        Returns:
            A dictionary with the metadata to create work items of a given project and type.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/createmeta/{project_id_or_key}/issuetypes/{issue_type_id}',
            params=params,
        )

    def add_attachment_to_issue(
        self, issue_id_or_key: str, filename, file_name: str, mime_type: str
    ) -> list[dict]:
        """Adds an attachment to an issue.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/#api-rest-api-3-issue-issueidorkey-attachments-post

        Attachments are posted as multipart/form-data (RFC 1867).

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            filename: the full name of the file to upload.
            file_name: the name of the file to upload.
            mime_type: the MIME type of the file.

        Returns:
            A list of dictionaries with the results.
        """
        return self.sync_client.make_request(  # type:ignore[return-value]
            method=httpx.post,
            url=f'issue/{issue_id_or_key}/attachments',
            headers={'X-Atlassian-Token': 'no-check'},
            files={'file': (file_name, open(filename, 'rb'), mime_type)},
        )

    async def delete_attachment(self, attachment_id: str) -> None:
        """Deletes an attachment from an issue.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/#api-rest-api-3-attachment-id-delete

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            `None`; HTTP 204 if successful or an exception otherwise.
        """
        await self.client.make_request(
            method=httpx.AsyncClient.delete, url=f'attachment/{attachment_id}'
        )
        return None

    async def get_issue_work_log(
        self,
        issue_id_or_key: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Retrieves work logs for an issue (ordered by created time), starting from the oldest worklog or from the
        worklog started on or after a date and time.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. The default is 50.

        Returns:
            A dictionary with the worklog of the work item.
        """
        params = {}
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        return await self.client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/{issue_id_or_key}/worklog',
            params=params,
        )
