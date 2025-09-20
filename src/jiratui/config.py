from contextvars import ContextVar
import os
from pathlib import Path

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


class ApplicationConfiguration(BaseSettings):
    jira_api_username: str
    """The username to use for connecting to the Jira API."""
    jira_api_token: str
    """The token to use for connecting to the Jira API."""
    jira_api_base_url: str
    """The base URL of the Jira API."""
    jira_api_version: int = DEFAULT_JIRA_API_VERSION
    """The version of the JiraAPI that JiraTUI wil use. The default is 3 but you can set to 2 if your Jira installation
    provides an older version of the API."""
    jira_user_group_id: str | None = None
    """The ID of the group that contains all (or most) of the Jira users in your Jira installation. This value is used
    as a fall back mechanism to fetch available users."""
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
