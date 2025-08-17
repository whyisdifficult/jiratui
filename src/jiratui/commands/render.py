from typing import Any

from rich.console import Console
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from jiratui.models import IssueComment, JiraIssueSearchResponse, JiraUser, JiraUserGroup
from jiratui.utils.adf2md.adf2md import adf2md


class Renderer:
    def render(self, console: Console, content: Any, **kwargs) -> None:
        raise NotImplementedError()


class CLIExceptionRenderer(Renderer):
    def render(self, console: Console, content: Any, **kwargs) -> None:
        if content:
            table = Table(title='Error Details')
            if 'work_item_key' in content:
                table.add_column('Work Item Key', style='cyan')
            if 'status_id' in content:
                table.add_column('Status ID', style='magenta')
            if 'comment_id' in content:
                table.add_column('Comment ID', style='magenta')
            if 'error_message' in content:
                table.add_column('Error', style='magenta')
            row: list = []
            if content.get('work_item_key', ''):
                row.append(content.get('work_item_key', ''))
            if content.get('status_id', ''):
                row.append(str(content.get('status_id', '')))
            if content.get('comment_id', ''):
                row.append(str(content.get('comment_id', '')))
            if content.get('error_message', ''):
                row.append(content.get('error_message', ''))
            table.add_row(*row)
            console.print(table)


class JiraUserRenderer(Renderer):
    def render(self, console: Console, content: list[JiraUser], **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No users found', 'bold red')))
            return
        table = Table(title='Jira Users')
        table.add_column('Account ID', style='cyan', no_wrap=True)
        table.add_column('Active', style='magenta')
        table.add_column('Name', style='green')
        table.add_column('Email Address', style='green')
        for user in content or []:
            table.add_row(user.account_id, str(user.active), user.display_name, user.email)
        console.print(table)


class JiraUserGroupRenderer(Renderer):
    def render(self, console: Console, content: list[JiraUserGroup], **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No users groups found', 'bold red')))
            return
        table = Table(title='Jira Users Groups')
        table.add_column('ID', style='cyan', no_wrap=True)
        table.add_column('Name', style='green')
        table.add_column('Total users in group?', style='yellow')
        for group in content or []:
            table.add_row(group.id, group.name, f'<CLI> users groups --group-id {group.id}')
        console.print(table)


class JiraIssueCommentRenderer(Renderer):
    def render(self, console: Console, content: IssueComment | None = None, **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No comment to show', 'bold red')))
            return

        try:
            comment_text = adf2md(content.body_as_dict())
        except Exception:
            comment_text = 'Unable to display the comment.'

        table = Table(title=f'Comment for Issue: {kwargs.get("issue_key")}')
        table.add_column('ID', style='cyan')
        table.add_column('Issue Key', style='magenta')
        table.add_column('Author', style='magenta')
        table.add_column('Created', style='magenta')
        table.add_column('Updated', style='magenta')
        table.add_column('Message', style='green')

        table.add_row(
            content.id,
            kwargs.get('issue_key'),
            f'{content.author.display_name} ({content.author.email})',
            content.created_on(),
            content.updated_on(),
            comment_text,
        )
        console.print(table)


class JiraIssueCommentTextRenderer(Renderer):
    def render(self, console: Console, content: IssueComment | None = None, **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No comment to show', 'bold red')))
            return
        try:
            comment_text = adf2md(content.body_as_dict())
        except Exception:
            comment_text = 'Unable to display the comment.'

        console.print(comment_text)
        console.print(Rule())


class JiraIssueCommentsRenderer(Renderer):
    def render(self, console: Console, content: dict, **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No comment to show', 'bold red')))
            return

        table = Table(title=f'Comment for Issue: {kwargs.get("issue_key")}')
        table.add_column('ID', style='cyan')
        table.add_column('Issue Key', style='magenta')
        table.add_column('Author', style='magenta')
        table.add_column('Created', style='magenta')
        table.add_column('Updated', style='magenta')
        table.add_column('Message', style='green')

        console.print(f'Total Comments: {content.get("total")}')
        for comment in content.get('comments', []):
            try:
                comment_text = adf2md(comment.body_as_dict())
            except Exception:
                comment_text = 'Unable to display the comment.'
            table.add_row(
                comment.id,
                kwargs.get('issue_key'),
                f'{comment.author.display_name} ({comment.author.email})',
                comment.created_on(),
                comment.updated_on(),
                comment_text,
            )
        console.print(table)


class JiraIssueSearchRenderer(Renderer):
    def render(self, console: Console, content: JiraIssueSearchResponse, **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No issues to show', 'bold red')))
            return

        table = Table(title='Work Items')
        table.add_column('Key', style='magenta')
        table.add_column('Type', style='magenta')
        table.add_column('Created', style='magenta')
        table.add_column('Status (ID)', style='green')
        table.add_column('Reporter', style='magenta')
        table.add_column('Assignee', style='magenta')
        table.add_column('Summary', style='green')

        for issue in content.issues:
            table.add_row(
                issue.key,
                issue.issue_type.name,
                issue.created_on,
                issue.display_status(),
                issue.display_reporter(),
                issue.display_assignee(),
                issue.cleaned_summary(20),
            )
        console.print(table)


class JiraIssueMetadataRenderer(Renderer):
    def render(self, console: Console, content: dict, **kwargs) -> None:
        console.print(Rule())
        if not content:
            console.print(Text.assemble(('No issues to show', 'bold red')))
            return

        issue_key = kwargs.get('issue_key')

        table = Table(title=f'Valid work types for work item: {issue_key}')
        table.add_column('ID', style='magenta')
        table.add_column('Name', style='magenta')
        table.add_column('Current?', style='magenta')
        table.add_column('Description', style='magenta')
        for work_item_type in content.get('types', []):
            table.add_row(
                work_item_type.get('id'),
                work_item_type.get('name'),
                'Yes' if content.get('current_work_item_type') == work_item_type.get('id') else '',
                work_item_type.get('description'),
            )
        console.print(table)

        table = Table(title=f'Valid priority IDs for work item: {issue_key}')
        table.add_column('ID', style='magenta')
        table.add_column('Name', style='magenta')
        table.add_column('Current?', style='magenta')
        table.add_column('Example', style='green')
        for priority in content.get('priorities', []):
            table.add_row(
                priority.get('id'),
                priority.get('name'),
                'Yes' if content.get('current_priority') == priority.get('id') else '',
                f'<CLI> issues update <ITEM-KEY> --priority-id {priority.get("id")}',
            )
        console.print(table)

        table = Table(title=f'Valid status transitions for work item: {issue_key}')
        table.add_column('Transition ID', style='magenta')
        table.add_column('Status ID', style='magenta')
        table.add_column('Status Name', style='magenta')
        table.add_column('Current?', style='magenta')
        table.add_column('Example', style='green')
        for transition in content.get('transitions', []):
            table.add_row(
                transition.get('id'),
                transition.get('to_state').get('id'),
                transition.get('to_state').get('name'),
                'Yes'
                if content.get('current_state') == transition.get('to_state').get('id')
                else '',
                f'<CLI> issues update <ITEM-KEY> --status-id {transition.get("to_state").get("id")}',
            )
        console.print(table)
