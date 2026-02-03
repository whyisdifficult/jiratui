from datetime import date, datetime
from io import BufferedReader
import json
import logging
from typing import Any

import httpx
import magic

from jiratui.api.client import AsyncJiraClient, JiraClient, JiraTUIAsyncHTTPClient
from jiratui.api.utils import build_issue_search_jql
from jiratui.config import ApplicationConfiguration
from jiratui.constants import ISSUE_SEARCH_DEFAULT_MAX_RESULTS, LOGGER_NAME
from jiratui.exceptions import FileUploadException
from jiratui.models import WorkItemsSearchOrderBy


class JiraAPI:
    """Implements methods to connect to the Jira REST API provided by the Jira Cloud Platform.

    **Supported Versions**

    - https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#version
    - https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/#version

    **Versions**

    [Version 2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/) and
    [version 3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) of the API offer the same collection of
    operations. However, version 3 provides support for the
    [Atlassian Document Format (ADF)](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) in:

    - body in comments, including where comments are used in issue, issue link, and transition resources.
    - comment in work-logs.
    - description and environment fields in issues.
    - textarea type custom fields (multi-line text fields) in issues. Single line custom fields (textfield) accept a
    string and don't handle Atlassian Document Format content.
    """

    API_PATH_PREFIX = '/rest/api/3/'

    def __init__(
        self,
        base_url: str,
        api_username: str,
        api_token: str,
        configuration: ApplicationConfiguration,
    ):
        # Async JSON client
        self._client = AsyncJiraClient(
            base_url=f'{base_url.rstrip("/")}{self.API_PATH_PREFIX}',
            api_username=api_username,
            api_token=api_token.strip(),
            configuration=configuration,
        )
        # Sync JSON client - for uploading attachments
        self._sync_client = JiraClient(
            base_url=f'{base_url.rstrip("/")}{self.API_PATH_PREFIX}',
            api_username=api_username,
            api_token=api_token.strip(),
            configuration=configuration,
        )
        # Async HTTP client - for downloading attachments
        self._async_http_client = JiraTUIAsyncHTTPClient(
            base_url=f'{base_url.rstrip("/")}{self.API_PATH_PREFIX}',
            api_username=api_username,
            api_token=api_token.strip(),
            configuration=configuration,
        )
        self._base_url = base_url
        # this allows us to issue requests to different endpoints depending on whether Jira runs on the cloud (default)
        # or on-premises
        self.cloud = configuration.cloud if configuration.cloud is False else True
        self.logger = logging.getLogger(LOGGER_NAME)

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def client(self) -> AsyncJiraClient:
        return self._client

    @property
    def async_http_client(self) -> JiraTUIAsyncHTTPClient:
        return self._async_http_client

    @property
    def sync_client(self) -> JiraClient:
        return self._sync_client

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

        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url=f'project/{project_key}/statuses'
        )

    async def get_issue_types_for_user(self) -> list[dict]:
        """Retrieves all the issue types.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/#api-rest-api-3-issuetype-get

        Returns:
            A list of dictionaries with the details of the types of issues.
        """
        return await self._client.make_request(method=httpx.AsyncClient.get, url='issuetype')  # type:ignore[return-value]

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
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get, url='statuses/search', params=params
        )

    async def status(self) -> list[dict]:
        return await self._client.make_request(method=httpx.AsyncClient.get, url='status')  # type:ignore[return-value]

    async def get_project(self, key: str) -> dict:
        """Retrieves the details of a project.

        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-projectidorkey-get

        Args:
            key: the project ID or project key (case-sensitive).

        Returns:
            A dictionary with the details of the project.
        """
        return await self._client.make_request(method=httpx.AsyncClient.get, url=f'project/{key}')  # type:ignore[return-value]

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

        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        await self._client.make_request(
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
        await self._client.make_request(
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
        offset: int | None = None,
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
            offset: N/A
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

        return await self._client.make_request(  # type:ignore[return-value]
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

        Important: this is only available for the Jira cloud platform. For on-premises we need another way or to disable
        the feature.

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

        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url='expression/evaluate',
            data=json.dumps(payload),
        )

    async def global_settings(self) -> dict:
        """Retrieves the global settings in Jira.

        These settings determine whether optional features (for example, subtasks, time tracking, and others) are
        enabled. If time tracking is enabled, this operation also returns the time tracking configuration.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-settings/#api-rest-api-3-configuration-get

        Returns:
            A dictionary with the settings.
        """
        return await self._client.make_request(method=httpx.AsyncClient.get, url='configuration')  # type:ignore[return-value]

    async def server_info(self) -> dict:
        """Retrieves information of the Jira server.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-server-info/#api-group-server-info

        Returns:
            A dictionary with the details.
        """
        return await self._client.make_request(method=httpx.AsyncClient.get, url='serverInfo')  # type:ignore[return-value]

    async def myself(self) -> dict:
        """Retrieves information of the Jira user connecting to the Jira server.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-myself/#api-rest-api-3-myself-get

        Returns:
            A dictionary with the details.
        """
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        payload = self._build_payload_to_add_comment(message)
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url=f'issue/{issue_id_or_key}/comment',
            data=json.dumps(payload),
        )

    @staticmethod
    def _build_payload_to_add_comment(message: str) -> dict:
        return {
            'body': {
                'content': [{'content': [{'text': message, 'type': 'text'}], 'type': 'paragraph'}],
                'type': 'doc',
                'version': 1,
            }
        }

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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        await self._client.make_request(
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.put,
            url=f'issue/{issue_id_or_key}',
            data=json.dumps(data),
            params={'returnIssue': True},
        )

    async def create_work_item(self, fields: dict) -> dict:
        """Creates a work item.

        The current version of this method does not implement support for setting the value of the environment field.
        If we want to change this then we would need to take care of the difference in the format of the
        environment field for API v2 (does nto support ADF) and v3 (supports ADF).

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post

        Args:
            fields: a dictionary with the fields and their values to create the item.

        Returns:
            A dictionary with the details of the new item.
        """
        payload = {'fields': fields}
        return await self._client.make_request(  # type:ignore[return-value]
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
        return await self._client.make_request(  # type:ignore[return-value]
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
        await self._client.make_request(
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

        The current version of this method does not implement support for adding a comment in the link between the 2
        work items. If we want to change this then we would need to take care of the difference in the format of the
        comment field for API v2 (does nto support ADF) and v3 (supports ADF).

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
        await self._client.make_request(
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
        return await self._client.make_request(method=httpx.AsyncClient.get, url='issueLinkType')  # type:ignore[return-value]

    async def delete_issue_link(self, link_id: str) -> None:
        await self._client.make_request(method=httpx.AsyncClient.delete, url=f'issueLink/{link_id}')
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
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/createmeta/{project_id_or_key}/issuetypes/{issue_type_id}',
            params=params,
        )

    def add_attachment_to_issue(
        self,
        issue_id_or_key: str,
        filename,
        file_name: str,
        mime_type: str | None = None,
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

        with open(filename, 'rb') as file_to_upload:
            try:
                # attempt to detect the MIME type based on the content of the file
                detected_mime_type: str = self._detect_file_mime_type(file_to_upload)  # type:ignore
            except FileNotFoundError as e:
                self.logger.warning(
                    f'File not found. Unable to determine the MIME type of he file {filename}.'
                )
                raise FileUploadException(
                    f'The file {filename} was not found. Unable to upload it as attachment.'
                ) from e
            return self._sync_client.make_request(  # type:ignore[return-value]
                method=httpx.post,
                url=f'issue/{issue_id_or_key}/attachments',
                headers={'X-Atlassian-Token': 'no-check'},
                files={'file': (file_name, file_to_upload, detected_mime_type)},
            )

    @staticmethod
    def _detect_file_mime_type(file_to_upload: BufferedReader) -> str:
        return magic.from_buffer(file_to_upload.read(2028), mime=True)

    async def delete_attachment(self, attachment_id: str) -> None:
        """Deletes an attachment from an issue.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/#api-rest-api-3-attachment-id-delete

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            `None`; HTTP 204 if successful or an exception otherwise.
        """
        await self._client.make_request(
            method=httpx.AsyncClient.delete, url=f'attachment/{attachment_id}'
        )
        return None

    async def get_attachment(self, attachment_id: str) -> dict:
        """Retrieves an attachment (metadata).

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/#api-rest-api-3-attachment-id-get
            https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-attachments/#api-rest-api-2-attachment-id-get

        Args:
            attachment_id: the ID of the attachment.

        Returns:
            A dictionary with the metadata of the attachment.
        """
        return await self._client.make_request(
            method=httpx.AsyncClient.get, url=f'attachment/{attachment_id}'
        )

    async def get_attachment_content(self, attachment_id: str) -> Any:
        """Retrieves the contents of an attachment.

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/#api-rest-api-3-attachment-content-id-get
            https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-attachments/#api-rest-api-2-attachment-content-id-get

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            A bytes representation of the attachment's content.
        """
        return await self._async_http_client.make_request(
            method=httpx.AsyncClient.get,
            url=f'attachment/content/{attachment_id}',
            follow_redirects=True,
        )

    async def get_issue_work_log(
        self,
        issue_id_or_key: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Retrieves work logs for an issue (ordered by created time), starting from the oldest worklog or from the
        worklog started on or after a date and time.

        ```{important}
        Time tracking must be enabled in Jira, otherwise this operation returns an error. For more information, see
        [Configuring time tracking](https://confluence.atlassian.com/x/qoXKM).
        ```

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page. The default is 5000.

        Returns:
            A dictionary with the worklog of the work item.
        """
        params = {}
        if offset is not None:
            params['startAt'] = offset
        if limit is not None:
            params['maxResults'] = limit
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url=f'issue/{issue_id_or_key}/worklog',
            params=params,
        )

    async def add_issue_work_log(
        self,
        issue_id_or_key: str,
        time_spent: str,
        started: datetime,
        time_remaining: str | None = None,
        comment: str | None = None,
    ) -> dict:
        """Adds a worklog to an issue.

        ```{important}
        Time tracking must be enabled in Jira, otherwise this operation returns an error. For more information, see
        [Configuring time tracking](https://confluence.atlassian.com/x/qoXKM).
        ```

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-post

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            comment: a comment about the worklog. Optional when creating or updating a worklog.
            started: the datetime on which the worklog effort was started. Required when creating a worklog. Optional
            when updating a worklog.
            time_spent: the time spent working on the issue as days (#d), hours (#h), or minutes (#m or #). Required
            when creating a worklog if timeSpentSeconds isn't provided. Optional when updating a worklog. Cannot be
            provided if timeSpentSecond is provided.
            time_remaining: the value to set as the issue's remaining time estimate, as days (#d), hours (#h),
            or minutes (#m or #). For example, 2d. Required when adjustEstimate is new.

        Returns:
            A dictionary with the worklog's details.
        """
        payload: dict[str, Any] = {
            'started': started.isoformat(timespec='milliseconds').replace('+00:00', '+0000'),
            'timeSpent': time_spent,
        }
        if comment and (comment_payload := self._build_worklog_comment_payload(comment)):
            payload['comment'] = comment_payload
        params = {'adjustEstimate': 'auto'}
        if time_remaining:
            params = {'newEstimate': time_remaining, 'adjustEstimate': 'new'}
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url=f'issue/{issue_id_or_key}/worklog',
            data=json.dumps(payload),
            params=params,
        )

    async def delete_work_log(self, issue_id_or_key: str, worklog_id: str) -> bool:
        """Deletes a worklog from an issue.

        ```{important}
        Time tracking must be enabled in Jira, otherwise this operation returns an error. For more information, see
        [Configuring time tracking](https://confluence.atlassian.com/x/qoXKM).
        ```

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-id-delete

        Args:
            issue_id_or_key: the ID or key of the issue.
            worklog_id: the ID of the worklog.

        Returns:
            True if the operation succeeds.
        """
        await self._client.make_request(
            method=httpx.AsyncClient.delete,
            url=f'issue/{issue_id_or_key}/worklog/{worklog_id}',
        )
        return True

    @staticmethod
    def _build_worklog_comment_payload(message: str) -> dict:
        """Builds the payload required for adding/set a description/comment to a worklog when a worklog is added to a work item.

        Args:
            message: a comment about the worklog. Optional when creating or updating a worklog.

        Returns:
            A dictionary with the payload's data for setting the worklog's comment/description.
        """
        return {
            'content': [{'content': [{'text': message, 'type': 'text'}], 'type': 'paragraph'}],
            'type': 'doc',
            'version': 1,
        }

    async def get_fields(self) -> list[dict]:
        """Retrieves system and custom issue fields according to the following rules.

        - Fields that cannot be added to the issue navigator are always returned.
        - Fields that cannot be placed on an issue screen are always returned.
        - Fields that depend on global Jira settings are only returned if the setting is enabled. That is,
        timetracking fields, subtasks, votes, and watches.
        - For all other fields, this operation only returns the fields that the user has permission to view (that is,
        the field is used in at least one project that the user has Browse Projects project permission for.)

        See Also:
            https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get

        Returns:
            A list of dictionaries.
        """
        return await self._client.make_request(method=httpx.AsyncClient.get, url='field')

    async def get_label_suggestions(self, query: str = '') -> Any | None:
        """Get label suggestions from Jira.

        Args:
            query: search query to filter label suggestions

        Returns:
            List of label suggestions or None if request fails
        """
        return await self._client.get_label_suggestions(query)


class JiraAPIv2(JiraAPI):
    """Implements methods to connect to the REST API v2 exposed by the Jira Cloud Platform.

    **API Docs**: https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/#about

    This class implements methods for connecting to Jira REST API v2.
    """

    API_PATH_PREFIX = '/rest/api/2/'

    @staticmethod
    def _build_payload_to_add_comment(message: str) -> dict:
        return {'body': message}


class JiraDataCenterAPI(JiraAPI):
    """Implements the API exposed by the Jira Data Center (aka. on-premises) platform.

    **API Docs**: https://developer.atlassian.com/server/jira/platform/rest/v11001/intro/#gettingstarted
    """

    # see: https://developer.atlassian.com/server/jira/platform/rest/v11001/intro/#structure
    API_PATH_PREFIX = '/rest/api/2/'

    async def search_projects(
        self,
        offset: int | None = None,
        limit: int | None = None,
        query: str | None = None,
        order_by: str | None = None,
        keys: list[str] = None,
    ) -> dict:
        """Retrieves all projects visible for the currently logged-in user, i.e. all the projects the user has either
        'Browse projects' or 'Administer projects' permission. If no user is logged in, it returns all projects that
        are visible for anonymous users.

        See Also:
            - https://developer.atlassian.com/server/jira/platform/rest/v11000/api-group-project/#api-api-2-project-get
            - https://docs.atlassian.com/software/jira/docs/api/REST/1000.1580.0/#api/2/project-getAllProjects

        Args:
            offset: N/A
            limit: N/A
            order_by: N/A
            keys: N/A
            query: N/A

        Returns:
            A dictionary with the details of the projects.
        """
        data = await self._client.make_request(method=httpx.AsyncClient.get, url='project')  # type:ignore[return-value]
        return {'values': data, 'isLast': True}

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
        offset: int | None = None,
        limit: int | None = None,
        order_by: WorkItemsSearchOrderBy | None = None,
    ) -> dict:
        """Searches for issues using JQL. Recent updates might not be immediately visible in the returned search
        results.

        See Also:
            - https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-search/#api-api-2-search-post
            - https://docs.atlassian.com/software/jira/docs/api/REST/1000.1580.0/#api/2/search-search

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
            next_page_token: N/A
            offset: the index of the first issue to return (0-based)
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
        if offset:
            payload['startAt'] = offset

        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post, url='search', data=json.dumps(payload)
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
        # not supported in Jira DC
        raise NotImplementedError('This feature is not implemented in Jira Data Center platform.')

    async def server_info(self) -> dict:
        """Retrieves information of the Jira server.

        See Also:
            - https://docs.atlassian.com/software/jira/docs/api/REST/1000.1580.0/#api/2/serverInfo-getServerInfo
            - https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-serverinfo/#api-api-2-serverinfo-get

        Returns:
            A dictionary with the details.
        """
        return await super().server_info()

    async def myself(self) -> dict:
        """Retrieves information of the Jira user connecting to the Jira server.

        See Also:
            - https://docs.atlassian.com/software/jira/docs/api/REST/1000.1580.0/#api/2/myself-getUser
            - https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-myself/#api-group-myself

        Returns:
            A dictionary with the details.
        """
        return await super().myself()

    async def user_search(
        self,
        username: str | None = None,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Retrieves a list of active users that match the search string and property.

        See Also:
            - https://docs.atlassian.com/software/jira/docs/api/REST/9.17.0/#api/2/user-findUsers
            -

        Args:
            username: A query string used to search username, name or e-mail address.
            query: N/A.
            offset: the index of the first item to return.
            limit: the maximum number of items to return (limited to 1000).

        Returns:
            A list of dictionaries with the details of the users.
        """
        return await super().user_search(username=query or username, offset=offset, limit=limit)

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
            offset: N/A
            limit: the maximum number of items to return per page. Default is `50`.
            query: expects a username.
            Required, unless `username` or `accountId` is specified.

        Returns:
            A list of dictionaries with the details of the users.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params['maxResults'] = limit
        if project_keys:
            params['projectKeys'] = ','.join(project_keys)
        if query:
            params['username'] = query
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.get,
            url='user/assignable/multiProjectSearch',
            params=params,
        )

    async def get_attachment(self, attachment_id: str) -> dict:
        """Retrieves an attachment (metadata).

        See Also:
            https://docs.atlassian.com/software/jira/docs/api/REST/1000.1580.0/#api/2/attachment-getAttachment
            https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-attachment/#api-api-2-attachment-id-get

        Args:
            attachment_id: the ID of the attachment.

        Returns:
            JSON representation of the attachment meta-data. The representation does not contain the
            attachment itself, but contains a URI that can be used to download the actual attached file.
        """
        return await super().get_attachment(attachment_id)

    async def get_attachment_content(self, attachment_id: str) -> Any:
        """Retrieves the contents of an attachment.

        See Also:
            https://docs.atlassian.com/software/jira/docs/api/REST/1000.1580.0/#api/2/attachment
            https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-attachment/#api-api-2-attachment-id-get

        Args:
            attachment_id: The ID of the attachment.

        Returns:
            A bytes representation of the attachment's content; or `None` if the attachment can not be downloaded.
        """
        attachment: dict
        if attachment := await self.get_attachment(attachment_id):
            if content := attachment.get('content'):
                await self._async_http_client.make_request(
                    method=httpx.AsyncClient.get,
                    url=content,
                    follow_redirects=True,
                )
        return None

    @staticmethod
    def _build_payload_to_add_comment(message: str) -> dict:
        return {'body': message}

    async def get_issue_work_log(
        self,
        issue_id_or_key: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Retrieves all work logs for an issue. Work logs won't be returned if the Log work field is hidden for the
        project.

        See Also:
            https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-issue/#api-api-2-issue-issueidorkey-worklog-get

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            offset: N/A.
            limit: N/A.

        Returns:
            A dictionary with the worklog of the work item.
        """
        return await super().get_issue_work_log(issue_id_or_key)

    async def add_issue_work_log(
        self,
        issue_id_or_key: str,
        time_spent: str,
        started: datetime,
        time_remaining: str | None = None,
        comment: str | None = None,
    ) -> dict:
        """Adds a worklog to an issue.

        See Also:
            https://developer.atlassian.com/server/jira/platform/rest/v11001/api-group-issue/#api-api-2-issue-issueidorkey-worklog-post

        Args:
            issue_id_or_key: the case-sensitive key of the work item.
            comment: a comment about the worklog. Optional when creating or updating a worklog.
            started: the datetime on which the worklog effort was started. Required when creating a worklog. Optional
            when updating a worklog.
            time_spent: the time spent working on the issue as days (#d), hours (#h), or minutes (#m or #). Required
            when creating a worklog if timeSpentSeconds isn't provided. Optional when updating a worklog. Cannot be
            provided if timeSpentSecond is provided.
            time_remaining: required when 'new' is selected for adjustEstimate. e.g. "2d".

        Returns:
            A dictionary with the worklog's details.
        """
        payload = {
            'started': started.isoformat(timespec='milliseconds').replace('+00:00', '+0000'),
            'timeSpent': time_spent,
            'issueId': issue_id_or_key,
        }
        if comment:
            payload['comment'] = comment
        params = {'adjustEstimate': 'auto'}
        if time_remaining:
            params = {'newEstimate': time_remaining, 'adjustEstimate': 'new'}
        return await self._client.make_request(  # type:ignore[return-value]
            method=httpx.AsyncClient.post,
            url=f'issue/{issue_id_or_key}/worklog',
            data=json.dumps(payload),
            params=params,
        )
