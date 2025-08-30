from datetime import datetime
import json

from jiratui.config import CONFIGURATION
from jiratui.models import (
    Attachment,
    IssueComment,
    IssuePriority,
    IssueStatus,
    IssueType,
    JiraIssue,
    JiraSprint,
    JiraUser,
    Project,
    RelatedJiraIssue,
    TimeTracking,
)


def build_issue_instance(
    issue_id: str,
    issue_key: str,
    fields: dict,
    project: dict,
    reporter: dict,
    status: dict,
    assignee: dict | None = None,
    comments: list[IssueComment] | None = None,
    related_issues: list[RelatedJiraIssue] | None = None,
    parent_issue_key: str | None = None,
    priority: dict | None = None,
    edit_meta: dict | None = None,
) -> JiraIssue:
    """Builds an instance of `JiraIssue` with the details of a work item.

    Args:
        issue_id: the ID of the work item.
        issue_key: the case-sensitive key of the item.
        fields: a dictionary with the details of different fields associated to the item.
        project: a dictionary with the details of the item's project.
        reporter: a dictionary with the details of the item's reporter.
        status: a dictionary with the details of the item's status.
        assignee: a dictionary with the details of the item's assignee.
        comments: a list of comments associated to the item.
        related_issues: a list of related issues.
        parent_issue_key: the case-sensitive key of the parent issue.
        priority: a dictionary with the details of the item's priority.
        edit_meta: a dictionary with the details of the item's metadata for editing the item.

    Returns:
        An instance of `JiraIssue`.
    """
    tracking = None
    if time_tracking := fields.get('timetracking'):
        tracking = TimeTracking(
            original_estimate=time_tracking.get('originalEstimate'),
            remaining_estimate=time_tracking.get('remainingEstimate'),
            time_spent=time_tracking.get('timeSpent'),
            original_estimate_seconds=time_tracking.get('originalEstimateSeconds'),
            remaining_estimate_seconds=time_tracking.get('remainingEstimateSeconds'),
            time_spent_seconds=time_tracking.get('timeSpentSeconds'),
        )

    sprint: JiraSprint | None = None
    if sprint_custom_field_id := CONFIGURATION.get().custom_field_id_sprint:
        if sprint_ids := fields.get(sprint_custom_field_id):
            sprint = JiraSprint(
                id=sprint_ids[0].get('id'),
                name=sprint_ids[0].get('name'),
                active=sprint_ids[0].get('active'),
            )

    attachments: list[Attachment] = []
    for item in fields.get('attachment', []):
        creator = None
        if author := item.get('author'):
            creator = JiraUser(
                account_id=author.get('accountId'),
                active=author.get('active'),
                display_name=author.get('displayName'),
                email=author.get('emailAddress'),
            )
        attachments.append(
            Attachment(
                id=item.get('id'),
                filename=item.get('filename'),
                size=item.get('size'),
                created=datetime.fromisoformat(item.get('created'))
                if item.get('created')
                else None,
                mime_type=item.get('mimeType'),
                author=creator,
            )
        )

    return JiraIssue(
        id=issue_id,
        key=issue_key,
        summary=fields.get('summary', ''),
        description=fields.get('description'),
        project=Project(
            id=project.get('id'),
            name=project.get('name'),
            key=project.get('key'),
        )
        if project
        else None,
        created=datetime.fromisoformat(fields.get('created')) if fields.get('created') else None,
        updated=datetime.fromisoformat(fields.get('updated')) if fields.get('updated') else None,
        priority=IssuePriority(
            id=priority.get('id'),
            name=priority.get('name'),
        )
        if priority
        else None,
        status=IssueStatus(id=str(status.get('id')), name=status.get('name')),
        assignee=JiraUser(
            account_id=assignee.get('accountId'),
            active=assignee.get('active'),
            display_name=assignee.get('displayName'),
            email=assignee.get('emailAddress'),
        )
        if assignee
        else None,
        reporter=JiraUser(
            account_id=reporter.get('accountId'),
            active=reporter.get('active'),
            display_name=reporter.get('displayName'),
            email=reporter.get('emailAddress'),
        )
        if reporter
        else None,
        issue_type=IssueType(
            id=fields.get('issuetype', {}).get('id'),
            name=fields.get('issuetype', {}).get('name'),
        ),
        comments=comments,
        related_issues=related_issues,
        parent_issue_key=parent_issue_key,
        time_tracking=tracking,
        resolution=fields.get('resolution').get('name') if fields.get('resolution') else None,
        resolution_date=datetime.fromisoformat(fields.get('resolutiondate'))
        if fields.get('resolutiondate')
        else None,
        labels=[label.lower() for label in fields.get('labels', [])]
        if fields.get('labels')
        else None,
        attachments=attachments,
        sprint=sprint,
        edit_meta=edit_meta,
        due_date=datetime.strptime(fields.get('duedate'), '%Y-%m-%d').date()
        if fields.get('duedate')
        else None,
    )


def build_comments(raw_comments: list[dict]) -> list[IssueComment]:
    """Builds a list of `IssueComment`.

    Args:
        raw_comments: a list of dictionaries with the details of comments.

    Returns:
        A list of instances `IssueComment`.
    """
    comments: list[IssueComment] = []
    for comment in raw_comments:
        try:
            author = comment.get('author', {})
            update_author = comment.get('updateAuthor')
            comments.append(
                IssueComment(
                    id=comment.get('id'),
                    author=JiraUser(
                        account_id=author.get('accountId'),
                        display_name=author.get('displayName'),
                        active=author.get('active'),
                        email=author.get('emailAddress'),
                    ),
                    created=datetime.fromisoformat(comment.get('created'))
                    if comment.get('created')
                    else None,
                    updated=datetime.fromisoformat(comment.get('updated'))
                    if comment.get('updated')
                    else None,
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
        except Exception:
            continue
    return comments


def build_related_work_items(links: list[dict]) -> list[RelatedJiraIssue]:
    """Builds a list of `RelatedJiraIssue` representing the items related to another item.

    Args:
        links: a dictionary with the details of the related items.

    Returns:
        A list of `RelatedJiraIssue`.
    """
    related_issues: list[RelatedJiraIssue] = []
    for item in links:
        if inward_issue := item.get('inwardIssue', {}):
            try:
                related_issues.append(_build_related_inward_issue(item, inward_issue))
            except Exception:
                continue
        if outward_issue := item.get('outwardIssue', {}):
            try:
                related_issues.append(_build_related_outward_issue(item, outward_issue))
            except Exception:
                continue
    return related_issues


def _build_related_inward_issue(item: dict, inward_issue: dict) -> RelatedJiraIssue:
    return RelatedJiraIssue(
        id=item.get('id'),
        key=inward_issue.get('key'),
        summary=inward_issue.get('fields', {}).get('summary'),
        priority=IssuePriority(
            id=inward_issue.get('fields', {}).get('priority').get('id'),
            name=inward_issue.get('fields', {}).get('priority').get('name'),
        )
        if inward_issue.get('fields', {}).get('priority')
        else None,
        status=IssueStatus(
            id=str(inward_issue.get('fields', {}).get('status', {}).get('id')),
            name=inward_issue.get('fields', {}).get('status', {}).get('name'),
        ),
        issue_type=IssueType(
            id=inward_issue.get('fields', {}).get('issuetype', {}).get('id'),
            name=inward_issue.get('fields', {}).get('issuetype', {}).get('name'),
        ),
        link_type=item.get('type', {}).get('inward'),
        relation_type='inward',
    )


def _build_related_outward_issue(item: dict, outward_issue: dict) -> RelatedJiraIssue:
    return RelatedJiraIssue(
        id=item.get('id'),
        key=outward_issue.get('key'),
        summary=outward_issue.get('fields', {}).get('summary'),
        priority=IssuePriority(
            id=outward_issue.get('fields', {}).get('priority').get('id'),
            name=outward_issue.get('fields', {}).get('priority').get('name'),
        )
        if outward_issue.get('fields', {}).get('priority')
        else None,
        status=IssueStatus(
            id=str(outward_issue.get('fields', {}).get('status', {}).get('id')),
            name=outward_issue.get('fields', {}).get('status', {}).get('name'),
        ),
        issue_type=IssueType(
            id=outward_issue.get('fields', {}).get('issuetype', {}).get('id'),
            name=outward_issue.get('fields', {}).get('issuetype', {}).get('name'),
        ),
        link_type=item.get('type', {}).get('outward'),
        relation_type='outward',
    )
