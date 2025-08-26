import dataclasses
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import enum
from enum import Enum
import json

from tonalite import Config

config = Config(type_hooks={datetime: datetime.fromisoformat})


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
    scope_project: Project | None = None


@dataclass
class JiraUser(BaseModel):
    account_id: str
    active: bool
    display_name: str
    email: str | None = None

    @property
    def display_user(self) -> str:
        if email := self.email:
            return email
        elif name := self.display_name:
            return name
        return self.account_id


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
    body: str | None = None

    def short_metadata(self) -> str:
        if self.update_author:
            return (
                f'{datetime.strftime(self.created, "%Y-%m-%d %H:%M")} - {self.author.display_name}'
            )
        return datetime.strftime(self.created, '%Y-%m-%d %H:%M')

    def updated_on(self) -> str:
        if not self.update_author:
            return datetime.strftime(self.updated, '%Y-%m-%d %H:%M')
        return f'{datetime.strftime(self.updated, "%Y-%m-%d %H:%M")} by {self.update_author.display_name}'

    def created_on(self) -> str:
        return datetime.strftime(self.updated, '%Y-%m-%d %H:%M')

    def body_as_dict(self) -> dict | None:
        if not self.body:
            return None
        return json.loads(self.body)


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
    size: int
    mime_type: str
    created: datetime | None = None
    author: JiraUser | None = None

    @property
    def created_date(self) -> str:
        if self.created:
            return datetime.strftime(self.created, '%Y-%m-%d %H:%M')
        return ''

    @property
    def kb(self) -> Decimal | None:
        if not self.size:
            return None
        return Decimal(self.size / 1024).quantize(Decimal('0.01'))

    @property
    def display_author(self) -> str:
        if author := self.author:
            if email := author.email:
                return email
            elif name := author.display_name:
                return name
            return author.account_id
        return ''


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
    description: dict | None = None
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

    def short_title(self) -> str:
        return f'{self.key.strip()} - {self.summary.strip()}'

    def cleaned_summary(self, max_length: int | None = None) -> str:
        if max_length is not None:
            return f'{self.summary.strip()[:max_length]}...'
        return self.summary.strip()

    def display_status(self) -> str:
        if self.status:
            return f'{self.status.name} ({self.status.id})'
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
            return datetime.strftime(self.due_date, '%Y-%m-%d')
        return ''

    @property
    def parent_key(self) -> str:
        return self.parent_issue_key or ''

    @property
    def priority_name(self) -> str:
        return self.priority.name if self.priority else ''

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


@dataclass
class JiraServerInfo(BaseModel):
    base_url: str
    display_url_servicedesk_help_center: str
    display_url_confluence: str
    version: str
    deployment_type: str
    build_number: int
    build_date: str
    scm_info: str
    server_title: str
    default_locale: str
    server_time_zone: str
    server_time: str | None = None

    @property
    def base_url_or_server_title(self) -> str:
        if self.server_title:
            return self.server_title
        return self.base_url


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
    comment: dict | None = None

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
                return f'{self.author.display_user} logged {self.time_spent} on {datetime.strftime(self.updated, "%Y-%m-%d %H:%M")}'
            else:
                return f'{self.author.display_user} logged {self.time_spent}'
        else:
            if self.updated:
                return f'{self.author.display_user} logged {self.time_spent} on {datetime.strftime(self.updated, "%Y-%m-%d %H:%M")}'
            else:
                return f'{self.author.display_user} logged {self.time_spent}'


@dataclass
class PaginatedJiraWorklog(BaseModel):
    logs: list[JiraWorklog]
    max_results: int
    start_at: int
    total: int
