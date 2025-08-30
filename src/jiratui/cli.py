import asyncio
from datetime import datetime
import sys

import click
from pydantic import ValidationError
from rich.console import Console

from jiratui.app import JiraApp
from jiratui.commands.handler import CommandHandler
from jiratui.commands.render import (
    CLIExceptionRenderer,
    JiraIssueCommentRenderer,
    JiraIssueCommentsRenderer,
    JiraIssueCommentTextRenderer,
    JiraIssueMetadataRenderer,
    JiraIssueSearchRenderer,
    JiraUserGroupRenderer,
    JiraUserRenderer,
)
from jiratui.config import ApplicationConfiguration
from jiratui.exceptions import CLIException

console = Console()


@click.group()
def cli():
    pass


@cli.group(help='Use it to add, list or delete comments associated to work items.')
def comments():
    pass


@cli.group(help='Use it to search, update or delete work items.')
def issues():
    pass


@cli.group(help='Use it to search users and user groups.')
def users():
    pass


# -- WORK ITEMS --


@issues.command('search')
@click.option(
    '--project-key', '-p', type=str, help='A case-sensitive key that identifies a project.'
)
@click.option('--key', '-k', type=str, help='A case-sensitive key that identifies a work item.')
@click.option(
    '--assignee-account-id', '-u', type=str, help='The account ID of a user to filter work items.'
)
@click.option(
    '--limit',
    '-l',
    type=int,
    help='The number of work items to return. Default is 10 items within the last 15 days.',
)
@click.option(
    '--created-from',
    type=click.DateTime(['%Y-%m-%d']),
    help='Searches issues created from this date forward (inclusive). Expects YYYY-MM-DD',
)
@click.option(
    '--created-until',
    type=click.DateTime(['%Y-%m-%d']),
    help='Searches issues created until this date (inclusive). Expects YYYY-MM-DD',
)
def search_issues(
    project_key: str,
    key: str | None = None,
    assignee_account_id: str | None = None,
    limit: int | None = None,
    created_from: datetime | None = None,
    created_until: datetime | None = None,
) -> None:
    """Search work items."""
    if not project_key and not key:
        raise click.BadParameter(
            'One of --project-key or --key must be provided',
        )

    handler = CommandHandler()

    if key:
        with console.status('Fetching work item...'):
            try:
                response = handler.get_issue(
                    key=key.strip(),
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
                )
            except CLIException as e:
                console.print('Unable to find the requested work item.')
                renderer = CLIExceptionRenderer()
                renderer.render(console, e.get_extra_details())
            except Exception as e:
                console.print(f'An unknown error occurred while fetching the work item: {str(e)}')
            else:
                render = JiraIssueSearchRenderer()
                render.render(console, response)
            return

    with console.status('Searching work items...'):
        try:
            response = handler.search_issues(
                project_key=project_key,
                assignee_account_id=assignee_account_id,
                limit=limit,
                created_from=created_from.date() if created_from else None,
                created_until=created_until.date() if created_until else None,
            )
        except CLIException as e:
            console.print('An error occurred while searching for work items')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        except Exception as e:
            console.print(f'An unknown error occurred while searching for work items: {str(e)}')
        else:
            render = JiraIssueSearchRenderer()
            render.render(console, response)


@issues.command('metadata')
@click.argument('work-item-key')
def issue_metadata(work_item_key: str) -> None:
    """Retrieves metadata associated to the work item identified by WORK_ITEM_KEY.

    WORK_ITEM_KEY is the case-sensitive key that identifies the work item.
    """
    handler = CommandHandler()
    with console.status('Fetching metadata for the selected work item...'):
        try:
            metadata: dict = asyncio.run(handler.get_metadata(work_item_key))
        except CLIException as e:
            console.print(f'Unable to retrieve metadata for the given work item: {str(e)}')
        else:
            render = JiraIssueMetadataRenderer()
            render.render(console, metadata, issue_key=work_item_key)


@issues.command('update')
@click.argument('work-item-key')
@click.option('--summary', '-s', help='Text to set as the summary (aka. title) of the work item.')
@click.option(
    '--assignee-account-id',
    '-u',
    help='The account ID of the user to whom the work item will be assigned. Pass -u "" or -u null to unassign the work item.',
)
@click.option(
    '--due-date',
    '-d',
    type=click.DateTime(['%Y-%m-%d']),
    help='Update the due date of an issue. Expects YYYY-MM-DD',
)
@click.option(
    '--meta',
    is_flag=True,
    type=bool,
    default=False,
    help='Shows metadata for an issue. This is useful for updates.',
)
@click.option(
    '--status-id',
    '-t',
    type=int,
    help='The ID of the status to set for the work item. Use --meta for more details.',
)
@click.option(
    '--priority-id',
    '-p',
    type=int,
    help='The ID of the priority to set for the work item. Use --meta for more details.',
)
def update_issue(
    work_item_key: str,
    summary: str | None = None,
    assignee_account_id: str | None = None,
    due_date: datetime | None = None,
    meta: bool | None = None,
    status_id: int | None = None,
    priority_id: int | None = None,
):
    """Updates (some) fields of the work item identified by WORK_ITEM_KEY.

    WORK_ITEM_KEY is the case-sensitive key that identifies the work item we want to update.
    """
    handler = CommandHandler()

    if meta:
        try:
            metadata: dict = asyncio.run(handler.get_metadata(work_item_key))
        except CLIException as e:
            console.print(f'Unable to retrieve metadata for the given work item: {str(e)}')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        except Exception as e:
            console.print(
                f'An unknown error occurred while retrieving metadata for the given work item: {str(e)}'
            )
        else:
            render = JiraIssueMetadataRenderer()
            render.render(console, metadata, issue_key=work_item_key)
        return

    if not any([summary, due_date, status_id, priority_id]) and assignee_account_id is None:
        raise click.BadParameter(
            'One of --summary, --due-date, --status-id, --priority-id, --assignee-account-id must be provided',
        )

    if summary is not None:
        summary = summary.strip()
        if not summary:
            raise click.BadParameter('summary can not be empty')

    if status_id:
        with console.status('Trying to update the status of the work item...'):
            try:
                result: bool = asyncio.run(handler.update_issue_status(work_item_key, status_id))
            except CLIException as e:
                console.print(
                    'An error occurred when trying to update the status of the work item.'
                )
                console.print(f'Error: {str(e)}')
                renderer = CLIExceptionRenderer()
                renderer.render(console, e.get_extra_details())
            except Exception as e:
                console.print(
                    f'An unknown error occurred when trying to update the status of the work item: {str(e)}'
                )
            else:
                if result:
                    console.print('The status of the work item was updated successfully.')
                else:
                    console.print('Failed to update the status of the work item.')

    if summary or assignee_account_id or priority_id or due_date:
        with console.status('Trying to update the details of the work item...'):
            try:
                result = asyncio.run(
                    handler.update_issue(
                        work_item_key,
                        summary=summary,
                        assignee_account_id=assignee_account_id,
                        due_date=due_date.date() if due_date else None,
                        priority_id=priority_id,
                    ),
                )
            except CLIException as e:
                console.print('An error occurred when trying to update the selected work item.')
                console.print(f'Error: {str(e)}')
                renderer = CLIExceptionRenderer()
                renderer.render(console, e.get_extra_details())
            except Exception as e:
                console.print(f'Unable to update the selected work item. {str(e)}')
            else:
                if result:
                    console.print('Work item updated successfully.')
                else:
                    console.print('Work item not updated.')


# -- COMMENTS --


@comments.command('add')
@click.argument('work-item-key')
@click.argument('message')
def add_comment(message: str, work_item_key: str):
    """Adds a comment to the work item identified by WORK_ITEM_KEY.

    WORK_ITEM_KEY is the case-sensitive key that identifies the work item.
    MESSAGE is the message of the comment.
    """
    handler = CommandHandler()
    with console.status('Trying to add the comment to the issue...'):
        try:
            response = handler.add_comment(work_item_key, message)
        except CLIException as e:
            console.print('Unable to add the comment to the given issue.')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        else:
            render = JiraIssueCommentRenderer()
            render.render(console, response, issue_key=work_item_key)


@comments.command('list')
@click.argument('work-item-key')
@click.option(
    '--page',
    '-p',
    default=1,
    type=int,
    help='The page number we want to retrieve. The max number of items per page is 10',
)
@click.option('--comment-id', '-c', default=None, help='The ID of a comment')
def list_comments(work_item_key: str, page: int = 1, comment_id: str | None = None):
    """Lists the comments of the work item identified by WORK_ITEM_KEY.

    WORK_ITEM_KEY is the case-sensitive key that identifies the work item.
    """
    handler = CommandHandler()
    with console.status('Fetching comments for the issue...'):
        try:
            response = handler.get_comments(work_item_key, comment_id, page=page)
        except CLIException as e:
            console.print('Unable to retrieve the comments for the given issue')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        else:
            render = JiraIssueCommentsRenderer()
            render.render(console, response, issue_key=work_item_key)


@comments.command('show')
@click.argument('work-item-key')
@click.argument('comment-id')
def show_comment(work_item_key: str, comment_id: str) -> None:
    """Shows the text of a comment of the work item identified by WORK_ITEM_KEY.

    WORK_ITEM_KEY is the case-sensitive key that identifies the work item.
    COMMENT_ID the id of the comment whose text we want to view.
    """
    handler = CommandHandler()
    with console.status('Fetching comment...'):
        try:
            comment = handler.get_comment(work_item_key, comment_id)
        except CLIException as e:
            console.print('Unable to retrieve the comment.')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        else:
            render = JiraIssueCommentTextRenderer()
            render.render(console, comment, issue_key=work_item_key)


@comments.command('delete')
@click.argument('work-item-key')
@click.argument('comment-id')
def delete_comment(work_item_key: str, comment_id: str):
    """Deletes the comment with id COMMENT_ID of the work item identified by WORK_ITEM_KEY.

    WORK_ITEM_KEY is the case-sensitive key that identifies the work item.
    COMMENT_ID the id of the comment whose text we want to view.
    """
    handler = CommandHandler()
    with console.status('Trying to delete the comment...'):
        try:
            handler.delete_comment(work_item_key, comment_id)
            console.print('Comment deleted successfully.')
        except CLIException as e:
            console.print('Unable to delete the comment for the given issue.')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())


# -- APPLICATION --


@cli.command('ui')
@click.option('--project-key', '-p', default=None, help='A case-sensitive Jira project key.')
@click.option('--work-item-key', '-w', default=None, help='A case-sensitive work item key.')
@click.option(
    '--assignee-account-id',
    '-u',
    default=None,
    help='A Jira user account ID. Typically this would be your Jira account ID so user-related dropdowns can pre-select your user',
)
@click.option(
    '--jql-expression-id',
    '-j',
    default=None,
    help='The ID of a JQL expression as defined in the config.',
)
def ui(
    project_key: str | None = None,
    work_item_key: str | None = None,
    assignee_account_id: str | None = None,
    jql_expression_id: int | None = None,
):
    """Launches the Jira TUI application."""
    try:
        settings = ApplicationConfiguration()  # type: ignore[call-arg] # noqa
    except ValidationError as e:
        console.print(
            'There are undefined configuration values. Make sure your config file is correct.'
        )
        for _e in e.errors():
            if location := _e.get('loc'):
                console.print(f'Missing or misconfigured setting {location[0]}: {_e.get("msg")}')
        sys.exit(1)
    JiraApp(
        settings,
        project_key=project_key,
        user_account_id=assignee_account_id,
        jql_expression_id=jql_expression_id,
        work_item_key=work_item_key,
    ).run()


# -- USERS --


@users.command('search')
@click.argument('email_or_name')
def search_users(email_or_name: str):
    """Searches users by email or name. This is useful for getting the account ID of users.

    EMAIL_OR_NAME is the email address or name to search users.
    """
    handler = CommandHandler()
    with console.status('Searching Jira users...'):
        try:
            items = handler.users(email_or_name=email_or_name)
        except CLIException as e:
            console.print('Unable to retrieve users.')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        else:
            render = JiraUserRenderer()
            render.render(console, items)


@users.command('groups')
@click.option(
    '--group-ids',
    '-g',
    default=None,
    help='Retrieve the groups with these IDs. Accepts a comma-separated list of IDs.',
)
@click.option(
    '--group-names',
    '-n',
    default=None,
    help='Retrieve the groups with this name.  Accepts a comma-separated list of names.',
)
@click.option(
    '--page',
    '-p',
    type=int,
    default=1,
    help='The page number we want to retrieve. The max number of items per page is 25',
)
@click.option(
    '--group-id',
    default=None,
    help='Count the number of users in the group',
)
def search_users_groups(
    group_ids: str | None = None,
    group_names: str | None = None,
    group_id: str | None = None,
    page: int = 1,
) -> None:
    """Searches Jira users groups. Use it to find groups of users by name or ID. Useful for setting the config variable
    jira_user_group_id."""
    handler = CommandHandler()
    if group_id:
        # fetch the number of users in the group
        with console.status('Counting Jira users in the group...'):
            try:
                result = handler.total_users_in_group(group_id=group_id)
            except CLIException as e:
                console.print('Unable to retrieve the total number of users in the group.')
                renderer = CLIExceptionRenderer()
                renderer.render(console, e.get_extra_details())
            else:
                console.print(f'Number of users in group with ID {group_id}: {result}')
        return

    with console.status('Searching Jira user groups...'):
        # find Jira users groups
        try:
            items = handler.search_user_groups(
                page=page,
                group_ids=[gid.strip() for gid in group_ids.split(',')] if group_ids else None,
                group_names=[gn.strip() for gn in group_names.split(',')] if group_names else None,
            )
        except CLIException as e:
            console.print('Unable to retrieve user groups.')
            renderer = CLIExceptionRenderer()
            renderer.render(console, e.get_extra_details())
        else:
            render = JiraUserGroupRenderer()
            render.render(console, items)


def jiratuicli():
    cli()


if __name__ == '__main__':
    jiratuicli()
