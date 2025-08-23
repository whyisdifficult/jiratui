import asyncio
from datetime import date, datetime, timedelta
from typing import Any

from jiratui.api_controller.controller import APIController, APIControllerResponse
from jiratui.config import CONFIGURATION, ApplicationConfiguration
from jiratui.exceptions import (
    CLIException,
    UpdateWorkItemException,
    ValidationError,
)
from jiratui.models import (
    IssueComment,
    IssueTransition,
    JiraIssueSearchResponse,
    JiraUser,
    JiraUserGroup,
    WorkItemsSearchOrderBy,
)
from jiratui.utils.work_item_updates import (
    work_item_assignee_has_changed,
    work_item_priority_has_changed,
)

USERS_GROUPS_PER_PAGE = 25
COMMENTS_PER_PAGE = 10


class CommandHandler:
    def __init__(self):
        CONFIGURATION.set(ApplicationConfiguration())  # noqa
        self.api = APIController()

    def users(self, email_or_name: str) -> list[JiraUser]:
        """Searches Jira users by name or email.

        Args:
            email_or_name: the name of the user or email address to filter users. Substring matching is supported.

        Returns:
            A list of `JiraUser` instances.

        Raises:
            CLIException: if an error occurs while fetching the users.
        """
        if not email_or_name:
            raise CLIException('You need do provide a value (name or email) to search users.')
        response: APIControllerResponse = asyncio.run(
            self.api.search_users(email_or_name=email_or_name)
        )
        if not response.success:
            raise CLIException(f'An error occurred while searching for users: {response.error}')
        return response.result

    def search_user_groups(
        self,
        group_ids: list[str] | None = None,
        group_names: list[str] | None = None,
        page: int = 1,
    ) -> list[JiraUserGroup]:
        """Searches Jira user groups by name or Id.

        Args:
            group_ids: a list of group ids to retrieve.
            group_names: a list of group names to search. Group names are matched exact, i.e. substring matching is
            not supported.
            page: the page number to retrieve. The default is 1.

        Returns:
            A list of `JiraUserGroup` instances.

        Raises:
            CLIException: if an error occurs while fetching the groups.
        """
        offset = 0 if page <= 0 else (page - 1) * USERS_GROUPS_PER_PAGE
        response: APIControllerResponse = asyncio.run(
            self.api.find_groups(
                offset=offset,
                limit=USERS_GROUPS_PER_PAGE,
                groups_ids=group_ids,
                groups_names=group_names,
            )
        )
        if not response.success:
            raise CLIException(
                f'An error occurred while searching for user groups: {response.error}'
            )
        return response.result

    def total_users_in_group(self, group_id: str | None = None) -> int:
        """Counts the number of users in a group.

        Args:
            group_id: the id of the group.

        Returns:
            The number of users in the group.

        Raises:
            CLIException: if an error occurs while counting the users.
        """
        response: APIControllerResponse = asyncio.run(
            self.api.count_users_in_group(group_id=group_id)
        )
        if not response.success:
            raise CLIException(
                f'An error occurred while counting the users in the group: {response.error}'
            )
        return response.result

    def add_comment(self, key: str, message: str) -> IssueComment | None:
        """Adds a comment to a work item.

        Args:
            key: the (case-sensitive) key of the work item to which we want to add a comment.
            message: the message/content of the comment

        Returns:
            Nothing.

        Raises:
            CLIException: if an error occurs while counting the users.
        """
        response: APIControllerResponse = asyncio.run(self.api.add_comment(key, message))
        if response.success:
            return response.result
        raise CLIException(
            'An error occurred while adding a comment.',
            extra={'work_item_key': key, 'error_message': response.error},
        )

    def get_comments(self, key: str, comment_id: str | None = None, page: int = 1) -> dict | None:
        """Retrieves the details the comments associated to a work item.

        It allows retrieving the details of a single comment or a list of comments.

        Args:
            key: the (case-sensitive) key of the work item associated to the comment.
            comment_id: the ID of the comment we want to retrieve.
            page: the page number to retrieve. The default is 1 and the number of items per page is 10.

        Returns:
            A dictionary with the details of the comments or, the details of a single comment.

        Raises:
            CLIException: if an error occurs while getting the comment(s).
        """

        if comment_id:
            response: APIControllerResponse = asyncio.run(
                self.api.get_comment(issue_key_or_id=key, comment_id=comment_id)
            )
            if response.success:
                return {'comments': [response.result or []], 'total': 1}
            raise CLIException(
                'An error occurred while fetching the comments.',
                extra={
                    'work_item_key': key,
                    'error_message': response.error,
                    'comment_id': comment_id,
                },
            )

        offset = 0 if page <= 0 else (page - 1) * COMMENTS_PER_PAGE
        response = asyncio.run(
            self.api.get_comments(issue_key_or_id=key, offset=offset, limit=COMMENTS_PER_PAGE)
        )
        if response.success:
            return {'comments': response.result or [], 'total': len(response.result or [])}
        raise CLIException(
            'An error occurred while fetching the comments.',
            extra={'work_item_key': key, 'error_message': response.error},
        )

    def get_comment(self, key: str, comment_id: str) -> IssueComment | None:
        """Retrieves the details of a single comment.

        Args:
            key: the (case-sensitive) key of the work item associated to the comment.
            comment_id: the ID of the comment.

        Returns:
            An instance of `IssueComment` with the comment; `None` if the comment is not found.

        Raises:
            CLIException: if an error occurs while getting the comment(s).
        """
        response: APIControllerResponse = asyncio.run(
            self.api.get_comment(issue_key_or_id=key, comment_id=comment_id)
        )
        if response.success:
            return response.result or None
        raise CLIException(
            'An error occurred while fetching the comment.',
            extra={'work_item_key': key, 'error_message': response.error, 'comment_id': comment_id},
        )

    def delete_comment(self, key: str, comment_id: str) -> bool:
        """Deletes a comment.

        Args:
            key: the (case-sensitive) key of the work item associated to the comment.
            comment_id: the ID of the comment.

        Returns:
            `True` if the comment was deleted successfully.

        Raises:
            CLIException: if an error occurs while deleting the comment.
        """
        response: APIControllerResponse = asyncio.run(
            self.api.delete_comment(issue_key_or_id=key, comment_id=comment_id)
        )
        if not response.success:
            raise CLIException(
                'An error occurred while trying to delete the comment',
                extra={
                    'work_item_key': key,
                    'error_message': response.error,
                    'comment_id': comment_id,
                },
            )
        return True

    async def update_issue(
        self,
        key: str,
        summary: str | None = None,
        assignee_account_id: str | None = None,
        due_date: date | None = None,
        priority_id: int | None = None,
    ) -> bool | None:
        response: APIControllerResponse = await self.api.get_issue(issue_id_or_key=key)
        if not response.success or not response.result or not response.result.issues:
            raise CLIException(
                'Unable to find the work item',
                extra={'work_item_key': key, 'error_message': response.error},
            )

        issue = response.result.issues[0]

        updates: dict[str, Any] = {}
        if summary:
            updates['summary'] = summary
        if assignee_account_id == '' or (assignee_account_id and assignee_account_id.lower()) in [
            'null',
            'none',
        ]:
            # set to unassign the work item
            updates['assignee_account_id'] = None
        if work_item_assignee_has_changed(issue.assignee, assignee_account_id):
            updates['assignee_account_id'] = assignee_account_id
        if due_date:
            updates['due_date'] = str(due_date)
        if work_item_priority_has_changed(issue.priority, str(priority_id)):
            if priority_id is not None:
                updates['priority'] = priority_id
            else:
                raise CLIException(
                    'Unable to set the priority of the work item.',
                    extra={
                        'work_item_key': key,
                        'error_message': 'It is not allowed to unset the priority.',
                    },
                )

        if updates:
            try:
                result: APIControllerResponse = await self.api.update_issue(issue, updates)
            except UpdateWorkItemException as e:
                raise CLIException(
                    'Unable to update the work item',
                    extra={'work_item_key': key, 'error_message': str(e)},
                ) from e
            except ValidationError as e:
                raise CLIException(
                    'One or more fields are not valid',
                    extra={'work_item_key': key, 'error_message': str(e)},
                ) from e
            return result.result.success
        return False

    async def update_issue_status(self, key: str, status_id: int | None = None) -> bool:
        response: APIControllerResponse = await self.api.get_issue(issue_id_or_key=key)
        if not response.success or not response.result or not response.result.issues:
            raise CLIException(
                'Unable to find the work item',
                extra={
                    'work_item_key': key,
                    'error_message': response.error,
                    'status_id': status_id,
                },
            )

        issue = response.result.issues[0]

        response = await self.api.transition_issue_status(issue.key, str(status_id))
        if not response.success:
            raise CLIException(
                f'Unable to transition the selected work item to the status with ID: {status_id}.',
                extra={
                    'work_item_key': key,
                    'error_message': response.error,
                    'status_id': status_id,
                },
            )
        return True

    def search_issues(
        self,
        project_key: str,
        assignee_account_id: str | None = None,
        limit: int = 10,
        created_from: date | None = None,
        created_until: date | None = None,
    ) -> JiraIssueSearchResponse:
        response: APIControllerResponse = asyncio.run(
            self.api.search_issues(
                project_key=project_key,
                fields=[
                    'id',
                    'key',
                    'status',
                    'summary',
                    'created',
                    'updated',
                    'author',
                    'reporter',
                    'issuetype',
                    'assignee',
                ],
                assignee=assignee_account_id,
                limit=limit,
                created_from=created_from or (datetime.now().date() - timedelta(days=15)),
                created_until=created_until,
                order_by=WorkItemsSearchOrderBy.CREATED_DESC,
            )
        )
        if response.success:
            return response.result
        raise CLIException(response.error)

    def get_issue(self, key: str, fields: list[str] | None = None) -> JiraIssueSearchResponse:
        """Retrieves the details of a work item.

        Args:
            key: the (case-sensitive) key of the work item.
            fields: the list of fields we want to retrieve.

        Returns:
            An instance of `JiraIssueSearchResponse` with the details of the work item.

        Raises:
            CLIException: if an error occurs while getting the comment(s).
        """
        response: APIControllerResponse = asyncio.run(
            self.api.get_issue(issue_id_or_key=key, fields=fields)
        )
        if response.success:
            return response.result
        raise CLIException(
            'An error occurred while trying to retrieve the work item.',
            extra={'work_item_key': key, 'error_message': response.error},
        )

    async def get_metadata(self, key: str) -> dict:
        response: APIControllerResponse = await self.api.get_issue(issue_id_or_key=key)
        if not response.success:
            raise CLIException(
                response.error, extra={'work_item_key': key, 'error_message': response.error}
            )

        result: JiraIssueSearchResponse = response.result

        issue = result.issues[0]

        # retrieve metadata related to status transitions
        response = await self.api.transitions(issue.key)
        if not response.success:
            raise CLIException(
                response.error, extra={'work_item_key': key, 'error_message': response.error}
            )

        transitions: list[IssueTransition] = response.result or []

        # retrieve metadata related to updates of other fields
        available_issue_types: list[dict] = []
        priorities: list[dict] = []

        if fields := issue.edit_meta.get('fields', {}):
            if priority := fields.get('priority', {}):
                for allowed_priority in priority.get('allowedValues', []):
                    priorities.append(
                        {
                            'id': allowed_priority.get('id'),
                            'name': allowed_priority.get('name'),
                        }
                    )

            if issue_type := fields.get('issuetype', {}):
                for allowed in issue_type.get('allowedValues', []):
                    available_issue_types.append(
                        {
                            'id': allowed.get('id'),
                            'name': allowed.get('name'),
                            'description': allowed.get('description'),
                        }
                    )
        return {
            'types': available_issue_types,
            'transitions': [t.as_dict() for t in transitions],
            'current_state': issue.status.id if issue.status else None,
            'current_work_item_type': issue.issue_type.id if issue.issue_type else None,
            'current_priority': issue.priority.id if issue.priority else None,
            'priorities': priorities,
        }
