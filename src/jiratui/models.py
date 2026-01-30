import dataclasses
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import enum
from enum import Enum
from typing import Any

from atlas_doc_parser.api import parse_node

from jiratui.utils.adf_helpers import (
    extract_mention_references,
    fix_adf_text_with_marks,
    fix_codeblock_in_list,
    format_mention_as_link,
    replace_media_with_text,
)


def custom_as_dict_factory(data) -> dict:
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return {k: convert_value(v) for k, v in data}


def custom_as_json_dict_factory(data) -> dict:
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return str(obj)
        return obj

    return {k: convert_value(v) for k, v in data}


class JiraWorkItemFields(Enum):
    """The fields ids supported by JiraTUI whose values can be extracted from the details of a work item.

    Each of these Ids are keys in the `fields` dictionary that is part of the API response that retrieves a work item.
    """

    PROJECT = 'project'
    STATUS = 'status'
    ASSIGNEE = 'assignee'
    REPORTER = 'reporter'
    PRIORITY = 'priority'
    PARENT = 'parent'
    TIME_TRACKING = 'timetracking'
    ATTACHMENT = 'attachment'
    SUMMARY = 'summary'
    DESCRIPTION = 'description'
    CREATED = 'created'
    UPDATED = 'updated'
    ISSUE_TYPE = 'issuetype'
    ISSUE_LINKS = 'issuelinks'
    COMMENT = 'comment'
    RESOLUTION_DATE = 'resolutiondate'
    RESOLUTION = 'resolution'
    LABELS = 'labels'
    DUE_DATE = 'duedate'
    COMPONENTS = 'components'


class WorkItemsSearchOrderBy(enum.Enum):
    CREATED_ASC = 'created asc'
    CREATED_DESC = 'created desc'
    PRIORITY_ASC = 'priority asc'
    PRIORITY_DESC = 'priority desc'
    KEY_ASC = 'key asc'
    KEY_DESC = 'key desc'

    @classmethod
    def to_choices(cls):
        return [(item.value.title(), item.value) for item in cls]


class CustomFieldTypes(enum.Enum):
    TEXTAREA = 'com.atlassian.jira.plugin.system.customfieldtypes:textarea'


@dataclass
class BaseModel:
    def as_dict(self) -> dict:
        """Dumps dataclass into dictionary.

        In this case some objects may be dumped differently e.g. Decimal will be dumped to a string.
        """

        return dataclasses.asdict(self, dict_factory=custom_as_dict_factory)

    def as_json(self) -> dict:
        """Dumps dataclass into json dictionary.

        In this case some objects may be dumped differently eg. Decimal will be dumped to a string.
        """

        return dataclasses.asdict(self, dict_factory=custom_as_json_dict_factory)


@dataclass
class Project(BaseModel):
    id: str
    name: str
    key: str

    def __str__(self):
        return f'[{self.key}] {self.name}'


@dataclass
class JiraIssueField(BaseModel):
    id: str
    name: str
    custom: bool


@dataclass
class IssueStatus(BaseModel):
    id: str
    name: str
    description: str | None = None


@dataclass
class IssueType(BaseModel):
    id: str
    name: str
    hierarchy_level: int | None = None
    """Hierarchy level of the issue type."""
    scope_project: Project | None = None


@dataclass
class JiraUser(BaseModel):
    account_id: str
    active: bool
    display_name: str
    email: str | None = None
    username: str | None = None  # only applicable for Jira DC API

    @property
    def display_user(self) -> str:
        if email := self.email:
            return email
        elif name := self.display_name:
            return name
        return self.get_account_id()

    def get_account_id(self) -> str:
        return self.account_id or ''


@dataclass
class IssuePriority(BaseModel):
    id: str
    name: str


@dataclass
class IssueComment(BaseModel):
    id: str
    author: JiraUser
    created: datetime | None = None
    updated: datetime | None = None
    update_author: JiraUser | None = None
    body: dict | str | None = None

    def short_metadata(self) -> str:
        if self.update_author and self.created:
            return f'{self.created.strftime("%Y-%m-%d %H:%M")} - {self.author.display_name}'
        return self.created.strftime('%Y-%m-%d %H:%M') if self.created else ''

    def updated_on(self) -> str:
        if not self.update_author:
            return self.updated.strftime('%Y-%m-%d %H:%M') if self.updated else ''
        return (
            f'{self.updated.strftime("%Y-%m-%d %H:%M")} by {self.update_author.display_name}'
            if self.updated
            else ''
        )

    def created_on(self) -> str:
        return self.updated.strftime('%Y-%m-%d %H:%M') if self.updated else ''

    def get_body(self, base_url: str | None = None) -> str:
        if not self.body:
            return ''
        if isinstance(self.body, str):
            return self.body.strip()

        # Pre-process ADF: replace mediaSingle with inline text, fix strong/em marks, fix codeblocks in lists
        fixed_body = replace_media_with_text(self.body)
        fixed_body = fix_adf_text_with_marks(fixed_body)
        fixed_body = fix_codeblock_in_list(fixed_body)
        markdown = parse_node(fixed_body).to_markdown(ignore_error=True)

        # Post-process mentions: replace plain @Name with [@Name](url)
        mentions = extract_mention_references(self.body)
        for mention in mentions:
            plain_text = mention['text']
            link_text = format_mention_as_link(mention, base_url)
            markdown = markdown.replace(plain_text, link_text)

        return markdown


@dataclass
class RelatedJiraIssue(BaseModel):
    id: str
    key: str
    summary: str
    status: IssueStatus
    issue_type: IssueType
    link_type: str = ''
    relation_type: str = ''  # outward/inward
    priority: IssuePriority | None = None

    def short_title(self) -> str:
        return f'{self.key} - {self.summary}'

    @property
    def priority_name(self) -> str:
        return self.priority.name if self.priority else ''

    def cleaned_summary(self, max_length: int | None = None) -> str:
        if max_length is not None:
            return f'{self.summary.strip()[:max_length]}...'
        return self.summary.strip()

    def display_status(self) -> str:
        if self.status:
            return self.status.name
        return ''


@dataclass
class TimeTracking(BaseModel):
    original_estimate: str | None = None
    remaining_estimate: str | None = None
    time_spent: str | None = None
    original_estimate_seconds: int | None = None
    remaining_estimate_seconds: int | None = None
    time_spent_seconds: int | None = None


@dataclass
class Attachment(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    created: datetime | None = None
    author: JiraUser | None = None

    @property
    def created_date(self) -> str:
        if self.created:
            return datetime.strftime(self.created, '%Y-%m-%d %H:%M')
        return ''

    def get_size(self) -> Decimal | None:
        if self.size is None:
            return None
        return Decimal(self.size / 1024).quantize(Decimal('0.01'))

    @property
    def display_author(self) -> str:
        if author := self.author:
            if email := author.email:
                return email
            elif name := author.display_name:
                return name
            elif username := author.username:
                return username
            return author.account_id or ''
        return ''

    def get_mime_type(self) -> str:
        return self.mime_type or ''


@dataclass
class JiraSprint(BaseModel):
    id: str
    name: str
    active: bool


@dataclass
class JiraBaseIssue(BaseModel):
    id: str
    key: str


@dataclass
class JiraIssueComponent(BaseModel):
    """A component that can be associated to a work item."""

    id: str
    name: str
    description: str | None = None


@dataclass
class JiraIssue(JiraBaseIssue):
    summary: str
    status: IssueStatus
    project: Project | None = None
    created: datetime | None = None
    updated: datetime | None = None
    due_date: date | None = None
    reporter: JiraUser | None = None
    issue_type: IssueType | None = None
    resolution_date: datetime | None = None
    resolution: str | None = None
    description: dict | str | None = None
    priority: IssuePriority | None = None
    assignee: JiraUser | None = None
    comments: list[IssueComment] | None = None
    related_issues: list[RelatedJiraIssue] | None = None
    parent_issue_key: str | None = None
    time_tracking: TimeTracking | None = None
    labels: list[str] | None = None
    attachments: list[Attachment] | None = None
    sprint: JiraSprint | None = None
    edit_meta: dict | None = None
    """a dictionary with the issue's edit metadata"""
    custom_fields: dict[str, Any] | None = None
    """a dictionary with the value of the custom fields associated to the issue that support updates based on the
    issue's edit metadata"""
    additional_fields: dict[str, Any] | None = None
    """These are fields that are not custom but whose values are not stored in a specific field; like the ones
    above. These fields have a key without the prefix 'custom_' and, are rendered dynamically in the UI's update
    form."""
    components: list[JiraIssueComponent] | None = None

    def short_title(self) -> str:
        return f'{self.key.strip()} - {self.summary.strip()}'

    def cleaned_summary(self, max_length: int | None = None) -> str:
        if max_length is not None:
            if (stripped_summary := self.summary.strip()) and len(
                stripped_summary
            ) > max_length - 3:
                return f'{stripped_summary[: max_length - 3]}...'
        return self.summary.strip()

    def display_status(self) -> str:
        if self.status:
            return f'{self.status.name} ({self.status.id})'
        return ''

    @property
    def status_name(self) -> str:
        if self.status:
            return self.status.name
        return ''

    @property
    def assignee_display_name(self) -> str:
        if self.assignee:
            return self.assignee.display_name
        return ''

    @property
    def work_item_type_name(self) -> str:
        if self.issue_type:
            return self.issue_type.name
        return ''

    @property
    def sprint_name(self) -> str:
        if self.sprint:
            return self.sprint.name
        return ''

    def display_assignee(self) -> str:
        if assignee := self.assignee:
            if email := assignee.email:
                return email
            elif name := assignee.display_name:
                return name
            return assignee.account_id
        return ''

    @property
    def reporter_display_name(self) -> str:
        if self.reporter:
            return self.reporter.display_name
        return ''

    def display_reporter(self) -> str:
        if reporter := self.reporter:
            if email := reporter.email:
                return email
            elif name := reporter.display_name:
                return name
            return reporter.account_id
        return ''

    @property
    def resolved_on(self) -> str:
        if self.resolution_date:
            return datetime.strftime(self.resolution_date, '%Y-%m-%d %H:%M')
        return ''

    @property
    def created_on(self) -> str:
        if self.created:
            return datetime.strftime(self.created, '%Y-%m-%d %H:%M')
        return ''

    @property
    def display_due_date(self) -> str:
        if self.due_date:
            return self.due_date.strftime('%Y-%m-%d')
        return ''

    @property
    def parent_key(self) -> str:
        return self.parent_issue_key or ''

    @property
    def priority_name(self) -> str:
        return self.priority.name if self.priority else ''

    def get_field_edit_metadata(self, name: str) -> dict | None:
        """Retrieves the edit metadata for a field.

        Args:
            name: the name of a field.

        Returns:
            The metadata of the field; None if the metadata does not contain information of the field.
        """
        if not self.edit_meta:
            return None
        return self.edit_meta.get('fields', {}).get(name)

    def get_edit_metadata(self) -> dict | None:
        """Retrieves the edit metadata for all the fields of the issue.

        Returns:
            The metadata of the fields  associated to this issue that can be edited; None if no metadata is found.
        """
        if not self.edit_meta:
            return None
        return self.edit_meta.get('fields')

    def get_custom_field_value(self, field_id: str) -> Any | None:
        """Retrieves the value of a custom field.

        Args:
            field_id: the ID of a field.

        Returns:
            The value of the custom field.
        """
        if not field_id:
            return None
        if not self.custom_fields:
            return None
        return self.custom_fields.get(field_id)

    def get_custom_fields(self) -> dict[str, Any]:
        if self.custom_fields is None:
            return {}
        return self.custom_fields

    def get_additional_field_value(self, field_id: str) -> Any | None:
        """Retrieves the value of a "dynamic" field.

        Args:
            field_id: the ID of a field.

        Returns:
            The value of the "dynamic" field.
        """
        if not field_id:
            return None
        if not self.additional_fields:
            return None
        return self.additional_fields.get(field_id)

    def get_additional_fields(self) -> dict[str, Any]:
        if self.additional_fields is None:
            return {}
        return self.additional_fields

    def get_description(self, base_url: str | None = None) -> str:
        if not self.description:
            return ''
        if isinstance(self.description, str):
            return self.description.strip()

        # Pre-process ADF: replace mediaSingle with inline text, fix strong/em marks, fix codeblocks in lists
        fixed_description = replace_media_with_text(self.description)
        fixed_description = fix_adf_text_with_marks(fixed_description)
        fixed_description = fix_codeblock_in_list(fixed_description)
        markdown = parse_node(fixed_description).to_markdown(ignore_error=True)

        # Post-process mentions: replace plain @Name with [@Name](url)
        mentions = extract_mention_references(self.description)
        for mention in mentions:
            plain_text = mention['text']
            link_text = format_mention_as_link(mention, base_url)
            markdown = markdown.replace(plain_text, link_text)

        return markdown

    def __repr__(self) -> str:
        return f'id:{self.id} - key:{self.key}'


@dataclass
class IssueRemoteLink(BaseModel):
    id: str
    global_id: str
    relationship: str
    title: str
    summary: str
    application_name: str | None = None
    url: str | None = None
    status_title: str | None = None
    status_resolved: bool | None = None


@dataclass
class JiraIssueSearchResponse(BaseModel):
    issues: list[JiraIssue]
    next_page_token: str | None = None
    is_last: bool | None = None
    total: int | None = None
    offset: int | None = None


@dataclass
class JiraTimeTrackingConfiguration(BaseModel):
    default_unit: str
    time_format: str
    working_days_per_week: int
    working_hours_per_day: int

    def display_default_unit(self) -> str:
        return self.default_unit or ''

    def display_time_format(self) -> str:
        return self.time_format or ''

    def display_working_days_per_week(self) -> str:
        return str(self.working_days_per_week or '')

    def display_working_hours_per_day(self) -> str:
        return str(self.working_hours_per_day or '')


@dataclass
class JiraGlobalSettings(BaseModel):
    attachments_enabled: bool
    issue_linking_enabled: bool
    subtasks_enabled: bool
    unassigned_issues_allowed: bool
    voting_enabled: bool
    watching_enabled: bool
    time_tracking_enabled: bool
    time_tracking_configuration: JiraTimeTrackingConfiguration | None = None

    def display_attachments_enabled(self) -> str:
        return 'Yes' if self.attachments_enabled else 'No'

    def display_subtasks_enabled(self) -> str:
        return 'Yes' if self.subtasks_enabled else 'No'

    def display_issue_linking_enabled(self) -> str:
        return 'Yes' if self.issue_linking_enabled else 'No'

    def display_unassigned_issues_allowed(self) -> str:
        return 'Yes' if self.unassigned_issues_allowed else 'No'

    def display_voting_enabled(self) -> str:
        return 'Yes' if self.voting_enabled else 'No'

    def display_watching_enabled(self) -> str:
        return 'Yes' if self.watching_enabled else 'No'

    def display_time_tracking_enabled(self) -> str:
        return 'Yes' if self.time_tracking_enabled else 'No'


@dataclass
class JiraServerInfo(BaseModel):
    base_url: str
    version: str
    build_number: int
    build_date: str
    scm_info: str
    server_title: str
    deployment_type: str | None = None
    default_locale: str | None = None
    server_time_zone: str | None = None
    server_time: str | None = None
    display_url_servicedesk_help_center: str | None = None
    display_url_confluence: str | None = None

    @property
    def base_url_or_server_title(self) -> str:
        if self.server_title:
            return self.server_title
        return self.base_url

    def get_display_url_servicedesk_help_center(self) -> str:
        return self.display_url_servicedesk_help_center or ''

    def get_display_url_confluence(self) -> str:
        return self.display_url_confluence or ''

    def get_server_time(self) -> str:
        return self.server_time or ''

    def get_server_time_zone(self) -> str:
        return self.server_time_zone or ''

    def get_deployment_type(self) -> str:
        return self.deployment_type or ''

    def get_default_locale(self) -> str:
        return self.default_locale or ''

    def get_server_title(self) -> str:
        return self.server_title or ''

    def get_scm_info(self) -> str:
        return self.scm_info or ''

    def get_build_date(self) -> str:
        return self.build_date or ''

    def get_build_number(self) -> str:
        return str(self.build_number) if self.build_number is not None else ''

    def get_version(self) -> str:
        return self.version or ''


@dataclass
class JiraUserGroup(BaseModel):
    id: str
    name: str


@dataclass
class JiraMyselfInfo(BaseModel):
    account_type: str
    account_id: str
    active: bool
    display_name: str
    email: str | None = None
    groups: list[JiraUserGroup] | None = None
    username: str | None = (
        None  # Jira DC does not support accountId; instead it uses the username to identify users
    )

    @property
    def display_user(self) -> str:
        if email := self.email:
            return email
        elif name := self.display_name:
            return name
        return self.account_id

    @property
    def user_groups(self) -> str | None:
        if not self.groups:
            return None
        return ','.join([g.name for g in self.groups])

    def get_account_id(self) -> str:
        return self.account_id or ''

    def get_username(self) -> str:
        return self.username or ''


@dataclass
class UpdateIssueData(BaseModel):
    summary: str | None = None
    assignee_account_id: str | None = None
    priority_id: str | None = None
    status_id: str | None = None


@dataclass
class UpdateWorkItemResponse(BaseModel):
    success: bool
    updated_fields: list[str] | None = None


@dataclass
class IssueTransitionState(BaseModel):
    id: str
    name: str
    description: str | None = None


@dataclass
class IssueTransition(BaseModel):
    id: str
    name: str
    to_state: IssueTransitionState | None = None


@dataclass
class LinkIssueType(BaseModel):
    id: str
    name: str
    outward: str
    inward: str


@dataclass
class JiraWorklog(BaseModel):
    id: str
    issue_id: str
    started: datetime | None = None
    updated: datetime | None = None
    time_spent: str | None = None
    time_spent_seconds: int | None = None
    author: JiraUser | None = None
    update_author: JiraUser | None = None
    comment: dict | str | None = None
    """Jira DC API uses strings instead of ADF, which are represented as dictionaries."""

    def updated_on(self) -> str:
        if self.update_author:
            if self.updated:
                return f'{datetime.strftime(self.updated, "%Y-%m-%d %H:%M")} by {self.update_author.display_user}'
            else:
                return f'by {self.update_author.display_user}'
        return datetime.strftime(self.updated, '%Y-%m-%d %H:%M') if self.updated else ''

    def created_on(self) -> str:
        if self.author:
            if self.started:
                return f'{datetime.strftime(self.started, "%Y-%m-%d %H:%M")} by {self.author.display_user}'
            else:
                return f'by {self.author.display_user}'
        return datetime.strftime(self.started, '%Y-%m-%d %H:%M') if self.started else ''

    def display(self) -> str:
        if self.author:
            if self.updated:
                return f'{self.author.display_user} logged {self.time_spent} on {self.updated.strftime("%Y-%m-%d %H:%M")}'
            else:
                return f'{self.author.display_user} logged {self.time_spent}'
        else:
            if self.updated:
                return f'Logged {self.time_spent} on {self.updated.strftime("%Y-%m-%d %H:%M")}'
            else:
                return f'Logged {self.time_spent}'

    def get_comment(self, base_url: str | None = None) -> str:
        """Gets the value of the worklog's comment.

        Jira DC API uses strings instead of ADF. In these cases we simply return the string value. For Jira Cloud API
        the value of the comment is an ADF dictionary and, in these cases we need to convert it to Markdown.

        Args:
            base_url: Optional base URL of Jira instance for formatting mentions as links

        Returns:
            A string representation of the worklog's description.
        """
        if not self.comment:
            return ''
        if isinstance(self.comment, str):
            return self.comment.strip()
        # Pre-process ADF: replace mediaSingle with inline text, fix strong/em marks, fix codeblocks in lists
        fixed_comment = replace_media_with_text(self.comment)
        fixed_comment = fix_adf_text_with_marks(fixed_comment)
        fixed_comment = fix_codeblock_in_list(fixed_comment)
        markdown = parse_node(fixed_comment).to_markdown(ignore_error=True)

        # Post-process mentions: replace plain @Name with [@Name](url)
        mentions = extract_mention_references(self.comment)
        for mention in mentions:
            plain_text = mention['text']
            link_text = format_mention_as_link(mention, base_url)
            markdown = markdown.replace(plain_text, link_text)

        return markdown


@dataclass
class PaginatedJiraWorklog(BaseModel):
    logs: list[JiraWorklog]
    max_results: int
    start_at: int
    total: int


@dataclass
class JiraField(BaseModel):
    """Represents a Jira field as returned by the endpoint that retrieves fields.

    See: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    id: str
    """The ID of the field."""
    key: str
    """The key of the field."""
    name: str
    """The name of the field."""
    custom: bool
    """Whether the field is a custom field."""
    schema: dict
    untranslated_name: str | None = None
    """The name of the field without translations."""
