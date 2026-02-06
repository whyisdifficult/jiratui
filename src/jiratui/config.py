from contextvars import ContextVar
import os
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from jiratui.constants import (
    DEFAULT_JIRA_API_VERSION,
    ISSUE_SEARCH_DEFAULT_DAYS_INTERVAL,
    ISSUE_SEARCH_DEFAULT_MAX_RESULTS,
)
from jiratui.files import get_config_file
from jiratui.models import BaseModel, WorkItemsSearchOrderBy


class SSLConfiguration(BaseModel):
    """Configuration for SSL CA bundles and client-side certificates."""

    verify_ssl: bool = True
    """Indicates whether HTTP requests should use SSL validation."""
    ca_bundle: str | None = None
    """Path to the CA bundle file."""
    certificate_file: str | None = None
    """Path to the a client-side certificate file, e.g. cert.pem"""
    key_file: str | None = None
    """Path to the key file."""
    password: SecretStr | None = None
    """The password for the key file."""


class StylingConfiguration(BaseModel):
    """Configuration for styling components."""

    work_item_status_colors: dict[str, str] | None = None
    """Color definitions for displaying the status of work items in the search results.

    Keys are lowercase status names w/o blank spaces. Values are color names or hex codes.

    Example:
    work_item_status_colors:
        done: red
        in_review: green
        in_progress: '#FF0000'
    """

    work_item_type_colors: dict[str, str] | None = None
    """Color definitions for displaying the type of work items in the search results.

    Keys are lowercase status names w/o blank spaces. Values are color names or hex codes.

    Example:
    work_item_type_colors:
        task: red
        bug: '#FF0000'
    """

    work_item_priority_colors: dict[str, str] | None = None
    """Color definitions for displaying the priority of work items in the search results and in other components.

    Keys are lowercase status names w/o blank spaces. Values are color names or hex codes.

    Example:
    work_item_priority_colors:
        high: red
        highest: '#FF0000'
    """


class ApplicationConfiguration(BaseSettings):
    """The configuration for the JiraTUI application and CLI tool."""

    jira_api_username: str
    """The username to use for connecting to the Jira API."""
    jira_api_token: SecretStr
    """The token to use for connecting to the Jira API."""
    jira_api_base_url: str
    """The base URL of the Jira API."""
    jira_api_version: int = DEFAULT_JIRA_API_VERSION
    """The version of the JiraAPI that JiraTUI wil use. The default is 3 but you can set to 2 if your Jira installation
    provides an older version of the API."""
    cloud: bool = True
    """Set this to False if your Jira instance run on-premises."""
    use_bearer_authentication: bool = False
    """Set this to True if your Jira instance uses Bearer authentication instead of Basic authentication."""
    jira_user_group_id: str | None = None
    """The ID of the group that contains all (or most) of the Jira users in your Jira installation. This value is used
    as a fall back mechanism to fetch available users. This is only supported in the Jira Cloud Platform."""
    jira_base_url: str | None = None
    """This is the base URL of your Jira application. This is used for building the URLs of different web links in the
    Jira TUI application. Example: https://<hostname>.atlassian.net"""
    jira_account_id: str | None = None
    """The ID of the Jira user using the application. This is useful if you want the user selection dropdown widgets to
    automatically select your user from the options. It is also used as the default reporter of any new work item that
    is created in the application."""
    search_results_per_page: int = ISSUE_SEARCH_DEFAULT_MAX_RESULTS
    """The number of results to show in the search results. The default is 30."""
    search_issues_default_day_interval: int = ISSUE_SEARCH_DEFAULT_DAYS_INTERVAL
    """This controls how many days worth of issues to fetch when no other search criteria has been defined."""
    show_issue_web_links: bool = True
    """If True (default) then the application will retrieve the remote links related to a work item."""
    ignore_users_without_email: bool = True
    """Controls whether Jira users without an email address configured should be included in the list of users and users
    assignable to projects and work items."""
    default_project_key_or_id: str | None = None
    """A case-sensitive string that identifies a Jira project. If set then the app will use is as the default selected
    project in the projects dropdown and will only fetch this project from your Jira instance."""
    active_sprint_on_startup: bool = False
    """If True, the Active Sprint checkbox will be enabled by default when the application starts, filtering search
    results to show only work items in the currently active sprint."""
    custom_field_id_sprint: str | None = None
    """The name of the custom field used by your Jira application to identify the sprints. Example: customfield_12345"""
    fetch_attachments_on_delete: bool = True
    """When this is True (default) the application will fetch the attachments of a work item after an attachment is
    deleted from the list of attachments. This makes the data more accurate but slower due to the extra request. When
    this is False the list of attachments is updated in place."""
    fetch_comments_on_delete: bool = True
    """When this is True (default) the application will fetch the comments of a work item after a comment is
    deleted from the list of comments. This makes the data more accurate but slower due to the extra request. When
    this is False the list of comments is updated in place."""
    pre_defined_jql_expressions: dict | None = None
    """A dictionary with pre-define JWL expressions to use in the JQL Expression Editor. Expects a mapping from
    user-defined IDs into a dictionary with a label and the expression. Example:

    1: {
        'label': 'Find work created by John and sort it by created date asc',
        'expression': 'creator = 'john' order by created asc'
    },
    2: {
        'label': 'Find work due on 2100-12-31 and for the production environment',
        'expression': 'dueDate = '2100-12-31' AND environment = 'production''
    }
    """
    jql_expression_id_for_work_items_search: int | None = None
    """If set to one of the expression IDs defined in pre_defined_jql_expressions then the app will use this expression
    to retrieve work items when not criteria and JQL query is provided by the user."""
    search_results_truncate_work_item_summary: int | None = None
    """When this is defined the summary of a work item will be truncated to the specified length when it is displayed in
    the search results."""
    search_results_style_work_item_status: bool = True
    """If True (default) the status of a work item will be styled when it is displayed in the search results."""
    search_results_style_work_item_type: bool = True
    """If True (default) the type of a work item will be styled when it is displayed in the search results."""
    on_start_up_only_fetch_projects: bool = True
    """When this is True the application will only load the list of available projects at startup. The list
    of status codes, users and work items types will be loaded when the user selects a project. If this is False then
    the application fill load (i.e. fetch from the API) available status codes, users and work items types in addition
    to the available projects. This may make the startup slower."""
    tui_title: str | None = None
    """An optional title for the application. This is displayed in the top bar."""
    tui_custom_title: str | None = None
    """A custom title for the application. If set, this overrides tui_title. If empty string, no title will be rendered."""
    tui_title_include_jira_server_title: bool = True
    """If `True` the application will fetch server information from the Jira API instance and use the server title or
    server base URL to build the title of the application. If set to `False` the title will be the default or, to the
    value of the `tui_custom_title` setting above; if defined."""
    log_file: str | None = None
    """The filename of the log file to use. If you set an empty string logging to a file is disabled."""
    log_level: str = 'WARNING'
    """The log level to use. Use Python's `logging` names: `CRITICAL`, `FATAL`, `ERROR`, `WARN`, `WARNING`, `INFO`,
    `DEBUG` and `NOTSET`."""
    attachments_source_directory: str = '/'
    """The directory to start the search of files that a user wants to attach to work items. The user will be able to
    navigate though the sub-directories."""
    confirm_before_quit: bool = False
    """If this is set to `True` then the application will show a pop-up screen so the user can confirm whether or not
    to quit the app. The default is `False` and the app simply exits."""
    theme: str | None = None
    """The name of the theme to use for the UI. Accept Textual themes."""
    search_results_page_filtering_enabled: bool = True
    """When this is True users will be able to filter search results by summary in the currently active results page
    using an input field."""
    search_results_page_filtering_minimum_term_length: int = 3
    """When search_results_page_filtering_enabled is True this value controls the minimum number of characters that the
    user needs to type in on order to filter results."""
    full_text_search_minimum_term_length: int = 3
    """When performing full-text search this value controls the minimum length of the search term provided by the
    user. JiraTUI will always enforce a vlue >= 3; even if you set a value of 0 here."""
    enable_advanced_full_text_search: bool = True
    """When this is True JiraTUI will use Jira ability to do full-text search not only in summary and description
    fields but in any text-based field, including comments. This may be slower. If this is False JiraTUI will only
    search items by summary and description fields."""
    ssl: SSLConfiguration | None = Field(default_factory=SSLConfiguration)
    """SSL configuration for client-side certificates and CA bundle."""
    search_results_default_order: WorkItemsSearchOrderBy = WorkItemsSearchOrderBy.CREATED_DESC
    """The default order for search results. Accepts values from WorkItemsSearchOrderBy enum: CREATED_ASC,
    CREATED_DESC, PRIORITY_ASC, PRIORITY_DESC, KEY_ASC, KEY_DESC."""
    git_repositories: dict | None = None
    """The Git repositories to create new branches based on work items. It expects a mapping from user-defined IDs into
    a dictionary with the name of the repository and the path to the directory that contains the .git directory.
    Example:
    1: {
        'name': 'The repo for my cool application',
        'path': '/my/repository/.git
    }
    """
    search_on_startup: bool = False
    """If True, triggers a search automatically when the UI starts. Can be set via CLI argument --search-on-startup."""
    enable_updating_additional_fields: bool = False
    """If True the app will allow the user to view and update additional fields."""
    update_additional_fields_ignore_ids: list[str] | None = None
    """When `enable_updating_additional_fields = True`, some custom fields and system fields with these ids or keys
    will be ignored and not show in the Details tab and will not be updated."""
    enable_images_support: bool = True
    """When this is set to `True` JiraTUI will attempt to display images attached to a work item in the Attachments
    tab."""
    styling: StylingConfiguration = Field(default_factory=StylingConfiguration)
    """Configuration for styling components like work item status, priorities and type colors."""

    model_config = SettingsConfigDict(
        extra='allow',
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        if jira_tui_config_file := os.getenv('JIRA_TUI_CONFIG_FILE'):
            conf_file = Path(jira_tui_config_file).resolve()
        else:
            conf_file = get_config_file()

        if not conf_file.exists():
            raise FileNotFoundError(f'Unable to find the config file you provided: {conf_file}')

        return (
            YamlConfigSettingsSource(settings_cls, yaml_file=conf_file),
            env_settings,
            dotenv_settings,
            init_settings,
        )


CONFIGURATION: ContextVar[ApplicationConfiguration] = ContextVar('configuration')
