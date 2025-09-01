from collections import defaultdict
import dataclasses
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
import logging
import mimetypes
import os
from pathlib import Path
from typing import Any

from jiratui.api.api import JiraAPI
from jiratui.api_controller.constants import (
    MAXIMUM_PAGE_NUMBER_LIST_GROUPS,
    MAXIMUM_PAGE_NUMBER_SEARCH_PROJECTS,
    RECORDS_PER_PAGE_LIST_GROUP_USERS,
    RECORDS_PER_PAGE_LIST_GROUPS,
    RECORDS_PER_PAGE_SEARCH_PROJECTS,
    RECORDS_PER_PAGE_SEARCH_USERS_ASSIGNABLE_TO_ISSUES,
    RECORDS_PER_PAGE_SEARCH_USERS_ASSIGNABLE_TO_PROJECTS,
)
from jiratui.api_controller.factories import (
    build_comments,
    build_issue_instance,
    build_related_work_items,
)
from jiratui.config import CONFIGURATION, ApplicationConfiguration
from jiratui.constants import ATTACHMENT_MAXIMUM_FILE_SIZE_IN_BYTES, LOGGER_NAME
from jiratui.exceptions import (
    ServiceInvalidResponseException,
    ServiceUnavailableException,
    UpdateWorkItemException,
    ValidationError,
)
from jiratui.models import (
    Attachment,
    BaseModel,
    IssueComment,
    IssueRemoteLink,
    IssueStatus,
    IssueTransition,
    IssueTransitionState,
    IssueType,
    JiraBaseIssue,
    JiraIssue,
    JiraIssueSearchResponse,
    JiraMyselfInfo,
    JiraServerInfo,
    JiraUser,
    JiraUserGroup,
    JiraWorklog,
    LinkIssueType,
    PaginatedJiraWorklog,
    Project,
    RelatedJiraIssue,
    UpdateWorkItemResponse,
    WorkItemsSearchOrderBy,
)


@dataclass
class APIControllerResponse(BaseModel):
    success: bool = True
    result: Any | None = None
    error: str | None = None

    def as_dict(self):
        return dataclasses.asdict(self)


class APIController:
    """A controller for the JirAPI to provide some additional functionality and integration of multiple endpoints."""

    def __init__(self, configuration: ApplicationConfiguration | None = None):
        self.config = CONFIGURATION.get() if not configuration else configuration
        self.api = JiraAPI(
            base_url=self.config.jira_api_base_url,
            api_username=self.config.jira_api_username,
            api_token=self.config.jira_api_token,
        )
        self.skip_users_without_email = self.config.ignore_users_without_email
        self.logger = logging.getLogger(LOGGER_NAME)

    async def get_project(self, key: str) -> APIControllerResponse:
        """Retrieves the details of a project by key.

        Args:
            key: the case-sensitive key of the project.

        Returns:
            An instance of `APIControllerResponse` with the details of the project in the `result key; `success=False`
            and the detail of the error if the project can not be retrieved.
        """

        try:
            response: dict = await self.api.get_project(key)
        except Exception as e:
            self.logger.error(
                'There was an error while fetching details of the project',
                extra={'error': str(e), 'key': key},
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(
            result=Project(
                id=str(response.get('id')), name=response.get('name'), key=response.get('key')
            ),
        )

    async def search_projects(
        self,
        query: str | None = None,
        order_by: str | None = None,
        keys: list[str] = None,
    ) -> APIControllerResponse:
        """Searches for projects using different filters.

        This method implements pagination in order to retrieve all the projects that satisfy the search criteria in a
        single operation. If an exception occurs while fetching any of the pages then the method will return the list
        of projects found so far with an additional error message.

        Args:
            query: filter the results using a literal string. Projects with a matching key or name are returned
            (case-insensitive).
            order_by: sort the results by a field: `key` (default), `category`, `issueCount`, `lastIssueUpdatedTime`,
            `name`, `owner`, `archivedDate`, `deletedDate`.
            keys: the project keys to filter the results by.

        Returns:
            An instance of `APIControllerResponse` with the list of `Project` instances. If an error occurs an
            instance of `APIControllerResponse` with the `error` message.
        """

        projects: list[Project] = []
        is_last = False
        i = 0
        while not is_last and i < MAXIMUM_PAGE_NUMBER_SEARCH_PROJECTS:
            try:
                response: dict = await self.api.search_projects(
                    offset=i * RECORDS_PER_PAGE_SEARCH_PROJECTS,
                    limit=RECORDS_PER_PAGE_SEARCH_PROJECTS,
                    query=query,
                    order_by=order_by,
                    keys=keys,
                )
            except Exception as e:
                self.logger.error(
                    'There was an error while searching projects',
                    extra={
                        'error': str(e),
                        'query': query,
                        'keys': keys,
                        'order_by': order_by,
                        'limit': RECORDS_PER_PAGE_SEARCH_PROJECTS,
                    },
                )
                return APIControllerResponse(result=projects, error=str(e))
            else:
                for project in response.get('values', []):
                    projects.append(
                        Project(
                            id=project.get('id'), key=project.get('key'), name=project.get('name')
                        )
                    )
                is_last = response.get('isLast')
                i += 1
        return APIControllerResponse(result=projects)

    async def get_project_statuses(self, project_key: str) -> APIControllerResponse:
        """Retrieves the statues applicable to issues of a project.

        Args:
            project_key: the case-sensitive key of a project.

        Returns:
            An instance of `APIControllerResponse` with the statuses grouped by type of issues. If an error occurs an
            instance of `APIControllerResponse` with the `error` message and `success = False`.
        """
        try:
            response: list[dict] = await self.api.get_project_statuses(project_key)
        except Exception as e:
            self.logger.error(
                'There was an error while fetching statuses associated to the project',
                extra={'error': str(e), 'project_key': project_key},
            )
            return APIControllerResponse(success=False, error=str(e))
        statuses_by_issue_type: dict[str, dict] = defaultdict(dict)
        for record in response:
            statuses_for_issue_type: list[IssueStatus] = []
            for status in record.get('statuses', []):
                statuses_for_issue_type.append(
                    IssueStatus(
                        id=str(status.get('id')),
                        name=status.get('name'),
                        description=status.get('description'),
                    )
                )
            # the statuses are grouped by issue type, as each project has a set of valid issue types
            # and each issue type has a set of valid statuses.
            statuses_by_issue_type[record.get('id')] = {
                'issue_type_name': record.get('name'),
                'issue_type_statuses': statuses_for_issue_type,
            }
        return APIControllerResponse(result=statuses_by_issue_type)

    async def status(self) -> APIControllerResponse:
        try:
            response: list[dict] = await self.api.status()
        except Exception as e:
            self.logger.error(
                'There was an error while fetching all available status codes',
                extra={'error': str(e)},
            )
            return APIControllerResponse(success=False, error=str(e))
        statuses: list[IssueStatus] = []
        for item in response:
            statuses.append(
                IssueStatus(
                    id=str(item.get('id')),
                    name=item.get('name'),
                    description=item.get('description'),
                )
            )
        return APIControllerResponse(result=statuses)

    # USERS GROUPS METHODS

    async def find_groups(
        self,
        offset: int = 0,
        limit: int = RECORDS_PER_PAGE_LIST_GROUPS,
        groups_ids: list[str] | None = None,
        groups_names: list[str] | None = None,
    ) -> APIControllerResponse:
        """Finds Jira users groups that match the given criteria.

        Args:
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page (number should be between 1 and 50).
            groups_ids: retrieve the groups with these IDs only.
            groups_names: retrieve the groups with these names only.

        Returns:
            An instance of `APIControllerResponse` with the list of `JiraUserGroup` instances. If an error occurs an
            instance of `APIControllerResponse` with the `error` message and `success = False`.
        """
        limit = (
            RECORDS_PER_PAGE_LIST_GROUPS
            if limit is None
            else min(limit, RECORDS_PER_PAGE_LIST_GROUPS)
        )
        groups: list[JiraUserGroup] = []
        try:
            response: dict = await self.api.get_groups_in_bulk(
                offset=offset,
                limit=limit,
                groups_ids=groups_ids,
                groups_names=groups_names,
            )
        except Exception as e:
            self.logger.error(
                'There was an error while searching users groups',
                extra={
                    'error': str(e),
                    'groups_ids': groups_ids,
                    'groups_names': groups_names,
                    'limit': min(limit, RECORDS_PER_PAGE_LIST_GROUPS),
                    'offset': offset,
                },
            )
            return APIControllerResponse(success=False, error=str(e))

        if response:
            groups = [
                JiraUserGroup(id=group.get('groupId'), name=group.get('name'))
                for group in response.get('values', [])
            ]
        return APIControllerResponse(result=groups)

    async def count_users_in_group(self, group_id: str) -> APIControllerResponse:
        """Counts the number of users in a Jira users group.

        Args:
            group_id: the ID of the Jira users group.

        Returns:
            The total number of users i the group.
        """
        try:
            response: dict = await self.api.get_users_in_group(group_id=group_id)
        except Exception as e:
            self.logger.error(
                'There was an error while trying to estimate the total number of users in a group',
                extra={
                    'error': str(e),
                    'group_id': group_id,
                },
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(result=int(response.get('total', 0)))

    async def list_all_active_users_in_group(self, group_id: str) -> APIControllerResponse:
        """Retrieves all the active users in a group.

        If an exception occurs while fetching any of the pages then the method will return the list of users found so
        far with an additional error message.

        Args:
            group_id: the ID of the Jira users group.

        Returns:
            An instance of `APIControllerResponse` with the list of `JiraUser` instances.
        """
        response: dict
        users: list[JiraUser] = []
        is_last = False
        i = 0
        while not is_last and i < MAXIMUM_PAGE_NUMBER_LIST_GROUPS:
            try:
                response = await self.api.get_users_in_group(
                    group_id=group_id,
                    offset=i * RECORDS_PER_PAGE_LIST_GROUP_USERS,
                    limit=RECORDS_PER_PAGE_LIST_GROUP_USERS,
                )
            except Exception as e:
                self.logger.error(
                    'There was an error while fetching all active users in a group.',
                    extra={
                        'error': str(e),
                        'group_id': group_id,
                        'offset': i * RECORDS_PER_PAGE_LIST_GROUP_USERS,
                        'limit': RECORDS_PER_PAGE_LIST_GROUP_USERS,
                    },
                )
                return APIControllerResponse(
                    result=sorted(users, key=lambda x: x.display_name or x.email or x.account_id),
                    error=str(e),
                )
            else:
                for user in response.get('values', []):
                    if user.get('active') is False:
                        continue
                    # skip users w/o email and w/o display name
                    if not user.get('emailAddress') and not user.get('displayName'):
                        continue
                    users.append(
                        JiraUser(
                            email=user.get('emailAddress'),
                            account_id=user.get('accountId'),
                            active=user.get('active'),
                            display_name=user.get('displayName'),
                        )
                    )
                is_last = response.get('isLast')
                i += 1
        return APIControllerResponse(
            result=sorted(users, key=lambda x: x.display_name or x.email or x.account_id)
        )

    # WORK ITEM TYPES

    async def get_issue_types_for_project(self, project_key: str) -> APIControllerResponse:
        """Retrieves the types of issues associated to a project.

        Args:
            project_key: the ID or (case-sensitive) key of the project whose issue types we want to retrieve.

        Returns:
            An instance of `APIControllerResponse` with the list of `IssueType` instances. If an error occurs an
            instance of `APIControllerResponse` with the `error` message.
        """
        try:
            project: dict = await self.api.get_project(project_key)
        except Exception as e:
            self.logger.error(
                'There was an error while fetching the types of issues associated to a project.',
                extra={
                    'error': str(e),
                    'project_key': project_key,
                },
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(
            result=[
                IssueType(id=str(item.get('id')), name=item.get('name'))
                for item in project.get('issueTypes', []) or []
            ]
        )

    async def get_issue_types(self) -> APIControllerResponse:
        """Retrieves all the types of issues relevant for any project.

        Warning: this may contain multiple issue types with the same name (different IDs though).

        Returns:
            An instance of `APIControllerResponse` with the list of `IssueType` instances. If an error occurs an
            instance of `APIControllerResponse` with the `error` message.
        """
        try:
            response: list[dict] = await self.api.get_issue_types_for_user()
        except Exception as e:
            self.logger.error(
                'There was an error while fetching types of issues.', extra={'error': str(e)}
            )
            return APIControllerResponse(success=False, error=str(e))
        else:
            projects_by_id: dict[str, Project] = {}
            projects: APIControllerResponse = await self.search_projects()
            if projects.success:
                # group projects by ID
                projects_by_id = {p.id: p for p in projects.result or []}

            result: list[IssueType] = []
            for item in response:
                scope_project: Project | None = None
                if (scope := item.get('scope', {})) and scope.get('type').lower() == 'project':
                    scope_project = projects_by_id.get(str(scope.get('project').get('id')))

                result.append(
                    IssueType(
                        id=str(item.get('id')),
                        name=item.get('name'),
                        scope_project=scope_project,
                    )
                )
            return APIControllerResponse(result=result)

    async def search_users(self, email_or_name: str) -> APIControllerResponse:
        """Searches users by email or name

        Args:
            email_or_name: the email or name to filter users

        Returns:
            An instance of `APIControllerResponse` with the list of `JiraUser` instances. If an error occurs an
            instance of `APIControllerResponse` with the `error` message.
        """
        try:
            response: list[dict] = await self.api.user_search(query=f'{email_or_name}')
        except Exception as e:
            self.logger.error(
                'There was an error while searching users',
                extra={'error': str(e), 'email_or_name': email_or_name},
            )
            return APIControllerResponse(success=False, error=str(e))

        users: list[JiraUser] = []
        for user in response:
            email = user.get('emailAddress')
            if self.skip_users_without_email and not email:
                continue
            users.append(
                JiraUser(
                    email=email,
                    account_id=user.get('accountId'),
                    active=user.get('active'),
                    display_name=user.get('displayName'),
                )
            )
        return APIControllerResponse(result=users)

    async def search_users_assignable_to_issue(
        self,
        issue_key: str,
        query: str | None = None,
        active: bool | None = True,
    ) -> APIControllerResponse:
        """Retrieves the users that can be assigned to a work item.

        Args:
            issue_key: the key (case-sensitive) of a work item.
            query: a string that is matched against user attributes, such as `displayName`, and `emailAddress`, to find
            relevant users. The string can match the prefix of the attribute's value. For example, `query=john` matches
            a user with a `displayName` of John Smith and a user with an `emailAddress` of johnson@example.com.
            active: if set to `True` (default) it will retrieve active users only.

        Returns:
            An instance of `APIControllerResponse` with the list of `JiraUser` instances. If an error occurs an
            instance of `APIControllerResponse` with the `error` message.
        """

        try:
            response: list[dict] = await self.api.user_assignable_search(
                issue_key=issue_key,
                query=query,
                offset=0,
                limit=RECORDS_PER_PAGE_SEARCH_USERS_ASSIGNABLE_TO_ISSUES,
            )
        except Exception as e:
            self.logger.error(
                'There was an error while fetching users assignable to an issue',
                extra={
                    'error': str(e),
                    'issue_key': issue_key,
                    'query': query,
                    'limit': RECORDS_PER_PAGE_SEARCH_USERS_ASSIGNABLE_TO_ISSUES,
                },
            )
            return APIControllerResponse(success=False, error=str(e))

        if active is not None:
            response = [item for item in response if item.get('active') == active]

        users: list[JiraUser] = []
        for user in response:
            email = user.get('emailAddress')
            if self.skip_users_without_email and not email:
                continue
            users.append(
                JiraUser(
                    email=email,
                    account_id=user.get('accountId'),
                    active=user.get('active'),
                    display_name=user.get('displayName'),
                )
            )
        return APIControllerResponse(
            result=sorted(users, key=lambda item: item.display_name or item.account_id)
        )

    async def search_users_assignable_to_projects(
        self,
        project_keys: list[str],
        query: str | None = None,
        active: bool | None = True,
    ) -> APIControllerResponse:
        """Retrieves the users that can be assigned to work items in multiple projects.

        Args:
            project_keys: a list of project keys (case-sensitive).
            query: a string that is matched against user attributes, such as `displayName`, and `emailAddress`, to find
            relevant users. The string can match the prefix of the attribute's value. For example, `query=john` matches
            a user with a `displayName` of John Smith and a user with an `emailAddress` of johnson@example.com.
            active: if set to `True` (default) it will retrieve active users only.

        Returns:
            An instance of `APIFacadeResponse` with a list of `JiraUser` and `success = True`. If an error occurs then
            `success = False` and the error message in the `error` key.
        """

        try:
            response: list[dict] = await self.api.user_assignable_multi_projects(
                project_keys=project_keys,
                query=query,
                offset=0,
                limit=RECORDS_PER_PAGE_SEARCH_USERS_ASSIGNABLE_TO_PROJECTS,
            )
        except Exception as e:
            self.logger.error(
                'There was an error while fetching users assignable to projects',
                extra={
                    'error': str(e),
                    'project_keys': project_keys,
                    'query': query,
                    'limit': RECORDS_PER_PAGE_SEARCH_USERS_ASSIGNABLE_TO_PROJECTS,
                },
            )
            return APIControllerResponse(success=False, error=str(e))

        if active is not None:
            response = [item for item in response if item.get('active') == active]

        users: list[JiraUser] = []
        for user in response:
            email = user.get('emailAddress')
            if self.skip_users_without_email and not email:
                continue
            users.append(
                JiraUser(
                    email=email,
                    account_id=user.get('accountId'),
                    active=user.get('active'),
                    display_name=user.get('displayName'),
                )
            )
        return APIControllerResponse(
            result=sorted(users, key=lambda item: item.display_name or item.account_id)
        )

    async def get_issue(
        self,
        issue_id_or_key: str,
        fields: list[str] | None = None,
        properties: str | None = None,
    ) -> APIControllerResponse:
        """Retrieves a work item (aka. Jira issue) by its key or id.

        Args:
            issue_id_or_key: the ID or case-sensitive key of the work item to retrieve.
            fields: a list of fields to return for the issue. This parameter accepts a comma-separated list. Use it
            to retrieve a subset of fields. Allowed values:
            - *all: Returns all fields.
            - *navigable: Returns navigable fields.
            - Any issue field, prefixed with a minus to exclude.
            properties: a list of issue properties to return for the issue. This parameter accepts a comma-separated
            list. Allowed values:
            - *all Returns all issue properties.
            - Any issue property key, prefixed with a minus to exclude.

        Returns:
            An instance of `APIFacadeResponse` with the issue and `success = True`. If an error occurs then
            `success = False` and the error message in the `error` key.
        """

        fields_strings: str | None = ','.join(fields) if fields else None
        try:
            issue: dict = await self.api.get_issue(
                issue_id_or_key=issue_id_or_key,
                fields=fields_strings,
                properties=properties,
            )
        except Exception as e:
            self.logger.error(
                'There was an error while fetching an issue',
                extra={
                    'error': str(e),
                    'issue_id_or_key': issue_id_or_key,
                    'fields': fields_strings,
                    'properties': properties,
                },
            )
            return APIControllerResponse(
                success=False,
                error=f'Failed to retrieve the work item {issue_id_or_key}: {str(e)}.',
            )
        else:
            issue_fields = issue.get('fields', {})
            issue_project = issue_fields.get('project', {})
            issue_status = issue_fields.get('status', {})
            issue_assignee: dict | None = issue_fields.get('assignee')
            issue_reporter: dict | None = issue_fields.get('reporter')
            issue_priority = issue_fields.get('priority')
            parent_issue_key = None
            if parent_issue := issue_fields.get('parent'):
                parent_issue_key = parent_issue.get('key')

            comments: list[IssueComment] = build_comments(
                issue_fields.get('comment', {}).get('comments', [])
            )
            related_issues: list[RelatedJiraIssue] = build_related_work_items(
                issue_fields.get('issuelinks', [])
            )
            try:
                instance: JiraIssue = build_issue_instance(
                    issue.get('id'),
                    issue.get('key'),
                    issue_fields,
                    issue_project,
                    issue_reporter,
                    issue_status,
                    issue_assignee,
                    comments,
                    related_issues,
                    parent_issue_key,
                    issue_priority,
                    issue.get('editmeta'),
                )
            except Exception as e:
                self.logger.error(
                    'There was an error while extracting data from an issue',
                    extra={'error': str(e), 'issue_id_or_key': issue_id_or_key},
                )
                return APIControllerResponse(
                    success=False,
                    error=f'Failed to extract the details of the requested work item {issue_id_or_key}: {str(e)}',
                )
            return APIControllerResponse(result=JiraIssueSearchResponse(issues=[instance]))

    def _build_criteria_for_searching_work_items(
        self,
        project_key: str | None = None,
        created_from: date | None = None,
        created_until: date | None = None,
        status: int | None = None,
        assignee: str | None = None,
        issue_type: int | None = None,
        jql_query: str | None = None,
    ) -> dict:
        search_criteria: dict = {}
        criteria_defined = any(
            [project_key, created_from, created_until, status, assignee, issue_type]
        )
        if not criteria_defined and not jql_query:
            if (expression_id := self.config.jql_expression_id_for_work_items_search) and (
                pre_defined_jql_expressions := self.config.pre_defined_jql_expressions
            ):
                if (expression_data := pre_defined_jql_expressions.get(expression_id)) and (
                    expression := expression_data.get('expression')
                ):
                    if (
                        cleaned_expression := expression.replace('\n', ' ').replace('\t', ' ')
                    ) and (jql_expression := cleaned_expression.strip()):
                        return {'jql': jql_expression, 'updated_from': None}

            return {
                'jql': None,
                'updated_from': (
                    datetime.now().date()
                    - timedelta(days=self.config.search_issues_default_day_interval)
                ),
            }
        elif jql_query:
            return {'jql': jql_query.strip(), 'updated_from': None}
        return search_criteria

    async def search_issues(
        self,
        project_key: str | None = None,
        created_from: date | None = None,
        created_until: date | None = None,
        status: int | None = None,
        assignee: str | None = None,
        issue_type: int | None = None,
        search_in_active_sprint: bool = False,
        jql_query: str | None = None,
        next_page_token: str | None = None,
        limit: int | None = None,
        order_by: WorkItemsSearchOrderBy | None = None,
        fields: list[str] | None = None,
    ) -> APIControllerResponse:
        """Searches for issues matching specified JQL query and other criteria.

        Args:
            project_key: the case-sensitive key of the project whose work items we want to search.
            created_from: search work items created from this date forward (inclusive).
            created_until: search work items created until this date (inclusive).
            status: search work items with this status.
            assignee: search work items assigned to this user's account ID.
            issue_type: search work items of this type.
            search_in_active_sprint: if `True` only work items that belong to the currently active sprint will be
            retrieved.
            jql_query: search work items using this (additional) JQL query.
            next_page_token: the token that identifies the next page of results. This helps implements pagination of
            results.
            limit: the maximum number of items to retrieve.
            order_by: an instance of `WorkItemsSearchOrderBy` to sort the results.
            fields: the fields to retrieve for every work item. It defaults to: `'id', 'key', 'status', 'summary',
            'issuetype'`

        Returns:
            An instance of `APIControllerResponse` with the work items found or, en error if the search can not be
            performed.
        """

        criteria: dict = self._build_criteria_for_searching_work_items(
            project_key=project_key,
            created_from=created_from,
            created_until=created_until,
            status=status,
            assignee=assignee,
            issue_type=issue_type,
            jql_query=jql_query,
        )

        try:
            response: dict = await self.api.search_issues(
                project_key=project_key,
                created_from=created_from,
                created_until=created_until,
                updated_from=criteria.get('updated_from'),
                status=status,
                assignee=assignee,
                issue_type=issue_type,
                search_in_active_sprint=search_in_active_sprint,
                jql_query=criteria.get('jql'),
                fields=fields if fields else ['id', 'key', 'status', 'summary', 'issuetype'],
                next_page_token=next_page_token,
                limit=limit,
                order_by=order_by,
            )
        except ServiceUnavailableException:
            return APIControllerResponse(
                success=False, error='Unable to connect to the Jira server.'
            )
        except ServiceInvalidResponseException:
            return APIControllerResponse(
                success=False, error='The response from the server contains errors.'
            )
        except Exception as e:
            return APIControllerResponse(
                success=False,
                error=f'There was an unknown error while searching for work items: {str(e)}',
            )

        issues: list[JiraIssue] = []
        for issue in response.get('issues', []):
            issue_fields = issue.get('fields', {})
            issue_project = issue_fields.get('project', {})
            issue_status = issue_fields.get('status', {})
            issue_assignee: dict | None = issue_fields.get('assignee')
            issue_reporter: dict | None = issue_fields.get('reporter')
            issue_priority = issue_fields.get('priority')
            parent_issue_key = None
            if parent_issue := issue_fields.get('parent'):
                parent_issue_key = parent_issue.get('key')

            comments: list[IssueComment] = build_comments(
                issue_fields.get('comment', {}).get('comments', [])
            )
            related_issues: list[RelatedJiraIssue] = build_related_work_items(
                issue_fields.get('issuelinks', [])
            )

            try:
                work_item = build_issue_instance(
                    issue.get('id'),
                    issue.get('key'),
                    issue_fields,
                    issue_project,
                    issue_reporter,
                    issue_status,
                    issue_assignee,
                    comments,
                    related_issues,
                    parent_issue_key,
                    issue_priority,
                )
                issues.append(work_item)
            except Exception:
                continue

        return APIControllerResponse(
            result=JiraIssueSearchResponse(
                issues=issues,
                next_page_token=response.get('nextPageToken'),
                is_last=response.get('isLast'),
            )
        )

    async def count_issues(
        self,
        project_key: str | None = None,
        created_from: date | None = None,
        created_until: date | None = None,
        status: int | None = None,
        assignee: str | None = None,
        issue_type: int | None = None,
        jql_query: str | None = None,
    ) -> APIControllerResponse:
        """Estimates the number of work items yield by a search.

        Args:
            project_key: the case-sensitive key of the project whose work items we want to search.
            created_from: search work items created from this date forward (inclusive).
            created_until: search work items created until this date (inclusive).
            status: search work items with this status.
            assignee: search work items assigned to this user's account ID.
            issue_type: search work items of this type.
            jql_query: search work items using this (additional) JQL query.

        Returns:
            An instance of `APIControllerResponse` with the count of work items or, en error if the estimation can not
            be calculated.
        """

        criteria: dict = self._build_criteria_for_searching_work_items(
            project_key=project_key,
            created_from=created_from,
            created_until=created_until,
            status=status,
            assignee=assignee,
            issue_type=issue_type,
            jql_query=jql_query,
        )

        try:
            response: dict = await self.api.work_items_search_approximate_count(
                project_key=project_key,
                created_from=created_from,
                created_until=created_until,
                updated_from=criteria.get('updated_from'),
                status=status,
                assignee=assignee,
                issue_type=issue_type,
                jql_query=criteria.get('jql'),
            )
        except Exception as e:
            return APIControllerResponse(
                success=False, error=f'Failed to count the number of work items: {str(e)}'
            )
        return APIControllerResponse(result=int(response.get('count', 0)))

    async def get_issue_remote_links(
        self, issue_key_or_id: str, global_id: str | None = None
    ) -> APIControllerResponse:
        """Retrieves the web links of a work item.

        Args:
            issue_key_or_id: the ID or case-sensitive key of a work item whose web links we want to retrieve.
            global_id: an optional global ID that identifies a Web Link.

        Returns:
            An instance of `APIControllerResponse` with the list of `IssueRemoteLink` or, `success = False` with
            an `error` key if there is an error.
        """

        try:
            response: list[dict] = await self.api.get_issue_remote_links(issue_key_or_id, global_id)
        except Exception as e:
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(
            result=[
                IssueRemoteLink(
                    id=str(item.get('id')),
                    global_id=item.get('globalId'),
                    relationship=item.get('relationship'),
                    title=item.get('object', {}).get('title'),
                    summary=item.get('object', {}).get('summary'),
                    url=item.get('object', {}).get('url'),
                    application_name=item.get('application', {}).get('name'),
                    status_title=item.get('object', {}).get('status', {}).get('title'),
                    status_resolved=item.get('object', {}).get('status', {}).get('resolved'),
                )
                for item in response
            ]
        )

    async def create_issue_remote_link(
        self, issue_key_or_id: str, url: str, title: str
    ) -> APIControllerResponse:
        if 'http' not in url:
            return APIControllerResponse(
                success=False, error='The url must be a full url including the http:// schema.'
            )
        if not title:
            title = url
        try:
            await self.api.create_issue_remote_link(issue_key_or_id, url, title)
        except Exception as e:
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse()

    async def delete_issue_remote_link(
        self, issue_key_or_id: str, link_id: str
    ) -> APIControllerResponse:
        """Deletes a web link associated to a work item.

        Args:
            issue_key_or_id: the (case-sensitive) key of the work item.
            link_id: the ID of the link we want to delete.

        Returns:
           An instance of `APIControllerResponse(success=True)` if the link was
           deleted; `APIControllerResponse(success=False)` otherwise.
        """
        try:
            await self.api.delete_issue_remote_link(issue_key_or_id, link_id)
        except Exception as e:
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse()

    async def server_info(self) -> APIControllerResponse:
        """Retrieves details of the Jira server instance.

        Returns:
            An instance of `APIControllerResponse(success=True)` with the details or,
            `APIControllerResponse(success=False)` if there is an error fetching the details.
        """
        try:
            response: dict = await self.api.server_info()
        except Exception as e:
            self.logger.error(
                'There was an error while fetching details of the Jira server instance.',
                extra={'error': str(e)},
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(
            result=JiraServerInfo(
                base_url=response.get('baseUrl'),
                display_url_servicedesk_help_center=response.get('displayUrlServicedeskHelpCenter'),
                display_url_confluence=response.get('displayUrlConfluence'),
                version=response.get('version'),
                deployment_type=response.get('deploymentType'),
                build_number=int(response.get('buildNumber', 0)),
                build_date=response.get('buildDate'),
                server_time=response.get('serverTime'),
                scm_info=response.get('scmInfo'),
                server_title=response.get('serverTitle'),
                default_locale=response.get('defaultLocale', {}).get('locale'),
                server_time_zone=response.get('serverTimeZone'),
            )
        )

    async def myself(self) -> APIControllerResponse:
        """Retrieves details of the Jira user connecting to the API.

        Returns:
            An instance of `APIControllerResponse(success=True)` with the details or,
            `APIControllerResponse(success=False)` if there is an error fetching the details.
        """
        try:
            response: dict = await self.api.myself()
        except Exception as e:
            self.logger.error(
                'There was an error while fetching details of the API user.',
                extra={'error': str(e)},
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(
            result=JiraMyselfInfo(
                account_id=response.get('accountId'),
                account_type=response.get('accountType'),
                active=response.get('active'),
                display_name=response.get('displayName'),
                email=response.get('emailAddress'),
                groups=[
                    JiraUserGroup(id=g.get('id'), name=g.get('name'))
                    for g in response.get('groups', {}).get('items', [])
                ],
            )
        )

    async def get_edit_metadata_for_issue(self, issue_key_or_id: str) -> dict:
        """Retrieve the metadata relevant for editing a work item.

        Args:
            issue_key_or_id: the (case-sensitive) key of the work item.

        Returns:
            A dictionary with the relevant metadata or, {} if there is an error fetching the data.
        """
        try:
            return await self.api.issue_edit_metadata(issue_key_or_id)
        except Exception as e:
            self.logger.error(
                'There was an error while fetching the edit-metadata of a work item.',
                extra={'error': str(e), 'issue_key_or_id': issue_key_or_id},
            )
            return {}

    async def update_issue(self, issue: JiraIssue, updates: dict) -> APIControllerResponse:
        """Updates a work item.

        This method supports updating the following fields:
        - Summary
        - Assignee
        - Status
        - Priority
        - Due Date
        - Labels

        Args:
            issue: the work item we want to update.
            updates: a dictionary with the Jira fields that we want to update and their corresponding values.

        Returns:
            An instance of `APIControllerResponse` with the result of the update, which may include a list of fields
            that were updated.

        Raises:
            UpdateWorkItemException: if the work item's edit metadata is missing.
            UpdateWorkItemException: if the work item's edit metadata does not include details of the fields that can
            be updated.
            UpdateWorkItemException: When any of the fields that we want to update do not support updates.
            ValidationError: If the summary field is empty.
        """

        if not (edit_issue_metadata := issue.edit_meta):
            raise UpdateWorkItemException('Missing expected metadata.')

        if not (fields := edit_issue_metadata.get('fields', {})):
            raise UpdateWorkItemException(
                'The selected work item does not include the required fields metadata.'
            )

        if 'summary' in updates:
            if not (summary := updates.get('summary')) or not summary.strip():
                raise ValidationError('The summary field can not be empty.')

        fields_to_update: dict[str, list] = {}

        if 'summary' in updates:
            # the issue's summary has changed
            if meta_summary := fields.get('summary', {}):
                if 'set' not in meta_summary.get('operations', {}):
                    raise UpdateWorkItemException(
                        'The field "summary" can not be updated for the selected work item.',
                        extra={'work_item_key': issue.key},
                    )
                fields_to_update[meta_summary.get('key')] = [{'set': updates.get('summary')}]
            else:
                raise UpdateWorkItemException(
                    'The field "summary" can not be updated for the selected work item.',
                    extra={'work_item_key': issue.key},
                )

        if 'due_date' in updates:
            # the issue's due date has changed
            if meta_due_date := fields.get('duedate', {}):
                if 'set' not in meta_due_date.get('operations', {}):
                    raise UpdateWorkItemException(
                        'The field "duedate" can not be updated for the selected work item.',
                        extra={'work_item_key': issue.key},
                    )
                fields_to_update[meta_due_date.get('key')] = [
                    {'set': updates.get('due_date') or None}
                ]
            else:
                raise UpdateWorkItemException(
                    'The field "due_date" can not be updated for the selected work item.',
                    extra={'work_item_key': issue.key},
                )

        if 'priority' in updates:
            # the issue's priority has changed
            if meta_priority := fields.get('priority', {}):
                if 'set' not in meta_priority.get('operations', {}):
                    raise UpdateWorkItemException(
                        'The field "priority" can not be updated for the selected work item.',
                        extra={'work_item_key': issue.key},
                    )
                fields_to_update[meta_priority.get('key')] = [
                    {'set': {'id': updates.get('priority')}}
                ]
            else:
                raise UpdateWorkItemException(
                    'The field "priority" can not be updated for the selected work item.',
                    extra={'work_item_key': issue.key},
                )

        if 'assignee_account_id' in updates:
            # the issue's assignee has changed
            if meta_assignee := fields.get('assignee', {}):
                if 'set' not in meta_assignee.get('operations', {}):
                    raise UpdateWorkItemException(
                        'The field "assignee" can not be updated for the selected work item.',
                        extra={'work_item_key': issue.key},
                    )
                fields_to_update[meta_assignee.get('key')] = [
                    {'set': {'accountId': updates.get('assignee_account_id')}}
                ]
            else:
                raise UpdateWorkItemException(
                    'The field "assignee_account_id" can not be updated for the selected work item.',
                    extra={'work_item_key': issue.key},
                )

        if 'labels' in updates:
            if meta_labels := fields.get('labels', {}):
                if 'set' in meta_labels.get('operations', {}):
                    fields_to_update[meta_labels.get('key')] = [{'set': updates.get('labels')}]

        if fields_to_update:
            response: dict = await self.api.update_issue(issue.key, fields_to_update)
            updated_fields: list[str] = []
            if fields := response.get('fields', {}):
                updated_fields = list(fields.keys())
            return APIControllerResponse(
                result=UpdateWorkItemResponse(success=True, updated_fields=updated_fields)
            )
        return APIControllerResponse(result=UpdateWorkItemResponse(success=True))

    async def transitions(self, issue_id_or_key: str) -> APIControllerResponse:
        """Retrieves the applicable (status) transitions of a work item.

        Args:
            issue_id_or_key: the (case-sensitive) key of the work item.

        Returns:
            An instance of `APIControllerResponse(success=True)` with the list of `IssueTransition` instances or,
            `APIControllerResponse(success=False)` if there is an error fetching the data.
        """
        try:
            response: dict = await self.api.transitions(issue_id_or_key)
        except Exception as e:
            self.logger.error(
                'There was an error while fetching the allowed status transitions of a work item.',
                extra={'error': str(e), 'issue_id_or_key': issue_id_or_key},
            )
            return APIControllerResponse(success=False, error=str(e))

        transitions: list[IssueTransition] = []
        for transition in response.get('transitions', []):
            if to_state := transition.get('to', {}):
                transitions.append(
                    IssueTransition(
                        id=str(transition.get('id')),
                        name=transition.get('name'),
                        to_state=IssueTransitionState(
                            id=str(to_state.get('id')),
                            name=to_state.get('name'),
                            description=to_state.get('description'),
                        ),
                    )
                )
        return APIControllerResponse(result=transitions)

    async def transition_issue_status(
        self, issue_id_or_key: str, status_id: str
    ) -> APIControllerResponse:
        """Transitions a work item to a new status.

        Args:
            issue_id_or_key: the (case-sensitive) key of the work item.
            status_id: the ID of the new status.

        Returns:
            An instance of `APIControllerResponse(success=True)` if the work item was transitioned;
            `APIControllerResponse(success=False)` if there is an error.
        """
        response: APIControllerResponse = await self.transitions(issue_id_or_key)
        if not response.success or not response.result:
            return APIControllerResponse(
                success=False,
                error=f'Unable to find valid status transitions for the selected item: {response.error}',
            )
        # extract the ID of the transition that corresponds to the selected status ID
        transition_id: str | None = None
        for transition in response.result:
            if transition.to_state.id == status_id:
                transition_id = transition.id
                break

        if transition_id is None:
            return APIControllerResponse(
                success=False, error='Unable to find a valid transition for the given status ID.'
            )

        try:
            await self.api.transition_issue(issue_id_or_key, transition_id)
        except Exception as e:
            self.logger.error(
                'There was an error while trying update the status of a work item.',
                extra={'error': str(e), 'issue_id_or_key': issue_id_or_key, 'status_id': status_id},
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse()

    async def get_comment(self, issue_key_or_id: str, comment_id: str) -> APIControllerResponse:
        """Retrieves the details of a comment.

        Args:
            issue_key_or_id: the case-sensitive key or id of a work item.
            comment_id: the id of the comment.

        Returns:
            An instance of `APIControllerResponse` with the `IssueComment` instance in the `result key;
            `success=False` and the detail of the error if one occurs.
        """
        try:
            comment: dict = await self.api.get_comment(issue_key_or_id, comment_id)
        except Exception as e:
            self.logger.error(
                'There was an error while trying to get the details of a comment.',
                extra={
                    'error': str(e),
                    'issue_key_or_id': issue_key_or_id,
                    'comment_id': comment_id,
                },
            )
            return APIControllerResponse(success=False, error=str(e))
        author = comment.get('author', {})
        update_author = comment.get('updateAuthor')
        return APIControllerResponse(
            result=IssueComment(
                id=comment.get('id'),
                author=JiraUser(
                    account_id=author.get('accountId'),
                    display_name=author.get('displayName'),
                    active=author.get('active'),
                    email=author.get('emailAddress'),
                ),
                created=datetime.fromisoformat(comment.get('created')),
                updated=datetime.fromisoformat(comment.get('updated')),
                update_author=JiraUser(
                    account_id=update_author.get('accountId'),
                    display_name=update_author.get('displayName'),
                    active=update_author.get('active'),
                    email=update_author.get('emailAddress'),
                )
                if update_author
                else None,
                body=json.dumps(comment.get('body')) if comment.get('body') else None,
            )
        )

    async def get_comments(
        self,
        issue_key_or_id: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> APIControllerResponse:
        """Retrieves the comments of a work item.

        Args:
            issue_key_or_id: the case-sensitive key or id of a work item.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page.

        Returns:
            An instance of `APIControllerResponse` with the list of `IssueComment` instances in the `result key;
            `success=False` and the detail of the error if one occurs.
        """
        try:
            response: dict = await self.api.get_comments(issue_key_or_id, offset, limit)
        except Exception as e:
            self.logger.error(
                'There was an error while trying to search the comments of a work item.',
                extra={'error': str(e), 'issue_key_or_id': issue_key_or_id},
            )
            return APIControllerResponse(
                success=False, error=f'Failed to retrieve the comments: {str(e)}'
            )
        comments: list[IssueComment] = []
        for record in response.get('comments', []):
            author = record.get('author', {})
            update_author = record.get('updateAuthor')
            comments.append(
                IssueComment(
                    id=record.get('id'),
                    created=datetime.fromisoformat(record.get('created'))
                    if record.get('created')
                    else None,
                    updated=datetime.fromisoformat(record.get('updated'))
                    if record.get('updated')
                    else None,
                    author=JiraUser(
                        account_id=author.get('accountId'),
                        active=author.get('active'),
                        display_name=author.get('displayName'),
                        email=author.get('emailAddress'),
                    ),
                    update_author=JiraUser(
                        account_id=update_author.get('accountId'),
                        active=update_author.get('active'),
                        display_name=update_author.get('displayName'),
                        email=update_author.get('emailAddress'),
                    )
                    if update_author
                    else None,
                    body=json.dumps(record.get('body')) if record.get('body') else None,
                )
            )
        return APIControllerResponse(result=comments)

    async def add_comment(self, issue_key_or_id: str, message: str) -> APIControllerResponse:
        """Adds a comment to a work item.

        Args:
            issue_key_or_id: the case-sensitive key or id of a work item.
            message: the text of the comment.

        Returns:
            An instance of `APIControllerResponse` with the result of the operation.
        """
        if not message:
            return APIControllerResponse(success=False, error='Missing required message.')
        try:
            response = await self.api.add_comment(issue_key_or_id, message)
        except Exception as e:
            self.logger.error(
                'There was an error while trying to add a comment',
                extra={'error': str(e), 'issue_key_or_id': issue_key_or_id},
            )
            return APIControllerResponse(success=False, error=str(e))
        author = response.get('author', {})
        update_author = response.get('updateAuthor')
        comment = IssueComment(
            id=response.get('id'),
            created=datetime.fromisoformat(response.get('created'))
            if response.get('created')
            else None,
            updated=datetime.fromisoformat(response.get('updated'))
            if response.get('updated')
            else None,
            author=JiraUser(
                account_id=author.get('accountId'),
                active=author.get('active'),
                display_name=author.get('displayName'),
                email=author.get('emailAddress'),
            ),
            update_author=JiraUser(
                account_id=update_author.get('accountId'),
                active=update_author.get('active'),
                display_name=update_author.get('displayName'),
                email=update_author.get('emailAddress'),
            )
            if update_author
            else None,
        )
        return APIControllerResponse(result=comment)

    async def delete_comment(self, issue_key_or_id: str, comment_id: str) -> APIControllerResponse:
        """Deletes a comment from a work item.

        Args:
            issue_key_or_id: the case-sensitive key or id of a work item.
            comment_id: the id of a comment.

        Returns:
            An instance of `APIControllerResponse` with the result of the operation.
        """
        try:
            await self.api.delete_comment(issue_key_or_id, comment_id)
        except Exception as e:
            self.logger.error(
                'There was an error while trying to delete a comment',
                extra={
                    'error': str(e),
                    'issue_key_or_id': issue_key_or_id,
                    'comment_id': comment_id,
                },
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse()

    async def link_work_items(
        self,
        left_issue_key: str,
        right_issue_key: str,
        link_type: str,
        link_type_id: str,
    ) -> APIControllerResponse:
        """Creates a link between 2 work items.

        Args:
            left_issue_key: the (case-sensitive) key of the work item.
            right_issue_key: the (case-sensitive) key of the work item.
            link_type: the type of link to create.
            link_type_id: the ID of the type of link.

        Returns:
            An instance of `APIControllerResponse(success=True)` if the work items were linked successfully;
            `APIControllerResponse(success=False)` if there is an error.
        """
        try:
            await self.api.create_issue_link(
                left_issue_key=left_issue_key,
                right_issue_key=right_issue_key,
                link_type=link_type,
                link_type_id=link_type_id,
            )
            return APIControllerResponse()
        except Exception as e:
            self.logger.error(
                'There was an error while trying to link 2 work items.',
                extra={
                    'error': str(e),
                    'left_issue_key': left_issue_key,
                    'link_type': link_type,
                    'link_type_id': link_type_id,
                },
            )
            return APIControllerResponse(success=False, error=str(e))

    async def delete_issue_link(self, link_id: str) -> APIControllerResponse:
        """Deletes the link between 2 work items.

        Args:
            link_id: the ID of the link to delete.

        Returns:
            An instance of `APIControllerResponse(success=True)` if the work items were unlinked successfully;
            `APIControllerResponse(success=False)` if there is an error.
        """
        try:
            await self.api.delete_issue_link(link_id)
        except Exception as e:
            self.logger.error(
                'There was an error while trying to delete the link of a work item',
                extra={'error': str(e), 'link_id': link_id},
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse()

    async def issue_link_types(self) -> APIControllerResponse:
        """Retrieves the types of links that can be created between 2 work items.

        Returns:
            An instance of `APIControllerResponse(success=True)` with the list of `LinkIssueType` instances;
            `APIControllerResponse(success=False)` if there is an error.
        """
        try:
            response: dict = await self.api.issue_link_types()
        except Exception as e:
            self.logger.error(
                'There was an error while fetching the types of work item links',
                extra={'error': str(e)},
            )
            return APIControllerResponse(success=False, error=str(e))
        link_types: list[LinkIssueType] = []
        for issue_link_type in response.get('issueLinkTypes', []):
            link_types.append(
                LinkIssueType(
                    id=issue_link_type.get('id'),
                    name=issue_link_type.get('name'),
                    inward=issue_link_type.get('inward'),
                    outward=issue_link_type.get('outward'),
                )
            )
        return APIControllerResponse(result=link_types)

    async def get_issue_create_metadata(
        self,
        project_id_or_key: str,
        issue_type_id: str,
    ) -> APIControllerResponse:
        """Retrieves the metadata relevant for creating work items of a project and of a certain type.

        Args:
            project_id_or_key: the (case-sensitive) key of the project.
            issue_type_id: the ID of the type of work item.

        Returns:
            An instance of `APIControllerResponse(success=True)` with the metadata;
            `APIControllerResponse(success=False)` if there is an error.
        """
        try:
            response = await self.api.get_issue_create_meta(project_id_or_key, issue_type_id)
            return APIControllerResponse(result=response)
        except Exception as e:
            self.logger.error(
                'There was an error while fetching the create-metadata of a work item',
                extra={
                    'error': str(e),
                    'issue_type_id': issue_type_id,
                    'project_id_or_key': project_id_or_key,
                },
            )
            return APIControllerResponse(success=False, error=str(e))

    async def create_work_item(self, data: dict) -> APIControllerResponse:
        """Creates a work item.

        Args:
            data: the data that includes the fields and values to create the work item.

        Returns:
            An instance of `APIControllerResponse` with an instance of `JiraBaseIssue` as the result. This includes the
            item id and key. If an error occurs then  `APIControllerResponse.success == False` and
            `APIControllerResponse.error` indicates the error.
        """
        fields = {}

        if assignee_account_id := data.get('assignee_account_id'):
            fields['assignee'] = {'id': assignee_account_id}

        if reporter_account_id := data.get('reporter_account_id'):
            fields['reporter'] = {'id': reporter_account_id}

        if issue_type_id := data.get('issue_type_id'):
            fields['issuetype'] = {'id': issue_type_id}

        if parent_key := data.get('parent_key'):
            fields['parent'] = {'key': parent_key}

        if project_key := data.get('project_key'):
            fields['project'] = {'key': project_key}

        if due_date := data.get('duedate'):
            fields['duedate'] = due_date

        if summary := data.get('summary'):
            fields['summary'] = summary

        if priority_id := data.get('priority'):
            fields['priority'] = {'id': priority_id}

        if description := data.get('description'):
            fields['description'] = {
                'content': [
                    {
                        'content': [
                            {
                                'type': 'text',
                                'text': description,
                            }
                        ],
                        'type': 'paragraph',
                    }
                ],
                'type': 'doc',
                'version': 1,
            }

        if not fields:
            return APIControllerResponse(
                success=False,
                error='The work item was not created because there are no details to create it.',
            )

        try:
            result: dict = await self.api.create_work_item(fields)
        except Exception as e:
            self.logger.error(
                'An error occurred while trying to create an item',
                extra={
                    'error_message': str(e),
                    'assignee_account_id': data.get('assignee_account_id'),
                    'reporter_account_id': data.get('reporter_account_id'),
                    'issue_type_id': data.get('issue_type_id'),
                    'parent_key': data.get('parent_key'),
                    'project_key': data.get('project_key'),
                    'duedate': data.get('duedate'),
                    'summary': data.get('summary'),
                    'priority': data.get('priority'),
                },
            )
            return APIControllerResponse(success=False, error=str(e))
        return APIControllerResponse(
            result=JiraBaseIssue(id=result.get('id'), key=result.get('key'))
        )

    def add_attachment(self, issue_key_or_id: str, filename: str) -> APIControllerResponse:
        """Adds a file attachment to a work item.

        Args:
            issue_key_or_id: the case-sensitive key or id of a work item.
            filename: the name of the file to attach.

        Returns:
            An instance of `APIControllerResponse` with the details of the attachment in the `result key; `success=False`
            and the detail of the error if the file can not be attached.
        """
        if not filename:
            return APIControllerResponse(
                success=False, error='Missing required filename parameter.'
            )

        # sanitize the file
        file_path = Path(filename)
        if not file_path.exists():
            self.logger.error(
                'Add attachment: the file provided does not exist', extra={'file_path': file_path}
            )
            return APIControllerResponse(success=False, error='The file provided does not exist.')

        if not file_path.is_file():
            self.logger.error(
                'Add attachment: the resource is not a file', extra={'file_path': file_path}
            )
            return APIControllerResponse(success=False, error='The path provided is not a file.')

        if (stats := file_path.stat()) and stats.st_size > ATTACHMENT_MAXIMUM_FILE_SIZE_IN_BYTES:
            self.logger.error(
                'Add attachment: file size exceeds the maximum allowed.',
                extra={
                    'file_path': file_path,
                    'size': stats.st_size,
                    'allowed': ATTACHMENT_MAXIMUM_FILE_SIZE_IN_BYTES,
                },
            )
            return APIControllerResponse(
                success=False, error='The file provided is larger than the maximum allowed size.'
            )

        head, name = os.path.split(filename)
        mime_type, type_encoding = mimetypes.guess_type(filename)
        try:
            response: list[dict] = self.api.add_attachment_to_issue(
                issue_key_or_id, filename, name, mime_type
            )
        except Exception as e:
            self.logger.error(
                'There was an error while attempting to add an attachment',
                extra={'error': str(e), 'issue_key_or_id': issue_key_or_id, 'filename': filename},
            )
            return APIControllerResponse(
                success=False, error=f'Failed to attach the file: {str(e)}'
            )
        else:
            creator = None
            if author := response[0].get('author'):
                creator = JiraUser(
                    account_id=author.get('accountId'),
                    active=author.get('active'),
                    display_name=author.get('displayName'),
                    email=author.get('emailAddress'),
                )
            attachment = Attachment(
                id=response[0].get('id'),
                filename=response[0].get('filename'),
                size=response[0].get('size'),
                mime_type=response[0].get('mimeType'),
                created=datetime.fromisoformat(response[0].get('created'))
                if response[0].get('created')
                else None,
                author=creator,
            )
        return APIControllerResponse(result=attachment)

    async def delete_attachment(self, attachment_id: str) -> APIControllerResponse:
        """Deletes an attachment.

        Args:
            attachment_id: the id of the attachment to delete.

        Returns:
            An instance of `APIControllerResponse` with the result of the operation.
        """
        try:
            await self.api.delete_attachment(attachment_id)
        except Exception as e:
            self.logger.error(
                'There was an error while attempting to delete an attachment',
                extra={'error': str(e), 'attachment_id': attachment_id},
            )
            return APIControllerResponse(
                success=False, error=f'Failed to delete the attachment: {str(e)}'
            )
        return APIControllerResponse()

    async def get_work_item_worklog(
        self,
        issue_key_or_id: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> APIControllerResponse:
        """Retrieves the work log of a work item.

        Args:
            issue_key_or_id: the case-sensitive key or id of a work item.
            offset: the index of the first item to return in a page of results (page offset).
            limit: the maximum number of items to return per page.

        Returns:
            An instance of `APIControllerResponse(success=True)` with the `JiraWorklog` entries;
            `APIControllerResponse(success=False)` if there is an error.
        """
        try:
            response: dict = await self.api.get_issue_work_log(issue_key_or_id, offset, limit)
        except Exception as e:
            return APIControllerResponse(success=False, error=str(e))

        logs: list[JiraWorklog] = []
        for work_log in response.get('worklogs', []):
            update_author = None
            if author := work_log.get('updateAuthor'):
                update_author = JiraUser(
                    account_id=author.get('accountId'),
                    display_name=author.get('displayName'),
                    active=author.get('active'),
                )
            author = None
            if value := work_log.get('author'):
                author = JiraUser(
                    account_id=value.get('accountId'),
                    display_name=value.get('displayName'),
                    active=value.get('active'),
                )
            logs.append(
                JiraWorklog(
                    id=work_log.get('id'),
                    issue_id=work_log.get('issueId'),
                    started=datetime.fromisoformat(work_log.get('started'))
                    if work_log.get('started')
                    else None,
                    updated=datetime.fromisoformat(work_log.get('updated'))
                    if work_log.get('updated')
                    else None,
                    time_spent=work_log.get('timeSpent'),
                    time_spent_seconds=work_log.get('timeSpentSeconds'),
                    author=author,
                    update_author=update_author,
                    comment=work_log.get('comment'),
                )
            )

        return APIControllerResponse(
            result=PaginatedJiraWorklog(
                logs=logs,
                start_at=response.get('startAt'),
                max_results=response.get('maxResults'),
                total=response.get('total'),
            )
        )
