<style>
.wy-nav-content{ max-width: 100%;}
</style>
# Settings

The following table describe all the configuration options you can set for the application. All the settings can be set
using env variables with the format `JIRA_TUI_<name>`, where `<name>` is the name of the setting in the table below.

Example: these are equivalent `JIRA_TUI_JIRA_API_USERNAME=foo@bar`, `jira_api_username=foo@bar`

The application uses the [XDG specification](https://specifications.freedesktop.org/basedir-spec/latest/) to locate
config (and log) files. The default name of the config file is `config.yaml`. You can override the location of the
config file via the env variable `JIRA_TUI_CONFIG_FILE`. The application will attempt to load the config
file in the following way:

1. If the variable `JIRA_TUI_CONFIG_FILE` is set it will use the file specified by it.
2. If not, if `XDG_CONFIG_HOME` is set then it will load the file `$XDG_CONFIG_HOME/jiratui/config.yaml`.
3. If not, it will attempt to load the file from `$HOME/.config/jiratui/config.yaml`.

| Name                                        | Type | Required          | Default Value | Description                                                                                                                                                                                                                                                                      |
|---------------------------------------------|------|-------------------|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `jira_api_username`                         | str  | {bdg-danger}`Yes` | None          | The username to use for connecting to the Jira API                                                                                                                                                                                                                               |
| `jira_api_token`                            | str  | {bdg-danger}`Yes` | None          | The token to use for connecting to the Jira API                                                                                                                                                                                                                                  |
| `jira_api_base_url`                         | str  | {bdg-danger}`Yes` | None          | The base URL of the Jira API                                                                                                                                                                                                                                                     |
| `jira_user_group_id`                        | str  | No                | None          | The ID of the group that contains all (or most) of the Jira users in your Jira installation. This value is used as a fall back mechanism to fetch available users                                                                                                                |
| `jira_base_url`                             | str  | No                | None          | This is the base URL of your Jira application. This is used for building the URLs of different web links in the Jira TUI application. Example: `https://<hostname>.atlassian.net`                                                                                                |
| `jira_account_id`                           | str  | No                | None          | The ID of the Jira user using the application. This is useful if you want the user selection dropdown widgets to automatically select your user from the options. It is also used as the default reporter of any new work item that is created in the application                |
| `search_results_per_page`                   | int  | No                | 30            | The number of results to show in the search results                                                                                                                                                                                                                              |
| `search_issues_default_day_interval`        | int  | No                | 15            | This controls how many days worth of issues to fetch when no other search criteria has been defined                                                                                                                                                                              |
| `show_issue_web_links`                      | bool | No                | True          | If `True` then the application will retrieve the remote links related to a work item                                                                                                                                                                                             |
| `ignore_users_without_email`                | bool | No                | True          | Controls whether Jira users without an email address configured should be included in the list of users and users assignable to projects and work items                                                                                                                          |
| `default_project_key_or_id`                 | str  | No                | None          | A case-sensitive string that identifies a Jira project. If set then the app will use is as the default selected project in the projects dropdown and will only fetch this project from your Jira instance                                                                        |
| `custom_field_id_sprint`                    | str  | No                | None          | The name of the custom field used by your Jira application to identify the sprints. Example: `customfield_12345`                                                                                                                                                                 |
| `fetch_attachments_on_delete`               | bool | No                | True          | When this is `True` the application will fetch the attachments of a work item after an attachment is deleted from the list of attachments. This makes the data more accurate but slower due to the extra request. When this is False the list of attachments is updated in place |
| `fetch_comments_on_delete`                  | bool | No                | True          | When this is `True` the application will fetch the comments of a work item after a comment is deleted from the list of comments. This makes the data more accurate but slower due to the extra request. When this is False the list of comments is updated in place              |
| `pre_defined_jql_expressions`               | dict | No                | None          | [See below](#configuring-pre-defined-jql-expressions)                                                                                                                                                                                                                            |
| `jql_expression_id_for_work_items_search`   | int  | No                | None          | If set to one of the expression IDs defined in `pre_defined_jql_expressions` then the app will use this expression to retrieve work items when not criteria and JQL query is provided by the user.                                                                               |
| `search_results_truncate_work_item_summary` | int  | No                | None          | When this is defined the summary of a work item will be truncated to the specified length when it is displayed in the search results                                                                                                                                             |
| `search_results_style_work_item_status`     | bool | No                | True          | If `True` the status of a work item will be styled when it is displayed in the search results                                                                                                                                                                                    |
| `search_results_style_work_item_type`       | bool | No                | True          | If `True` the type of a work item will be styled when it is displayed in the search results                                                                                                                                                                                      |
| `on_start_up_only_fetch_projects`           | bool | No                | True          | [See below](#fetching-only-projects-on-startup)                                                                                                                                                                                                                                  |
| `tui_title`                                 | str  | No                | None          | An optional title for the application. This is displayed in the top bar                                                                                                                                                                                                          |
| `tui_title_include_jira_server_title`       | bool | No                | True          | [See below](#include-jira-server-title-in-the-ui-title)                                                                                                                                                                                                                          |
| `attachments_source_directory`              | str  | No                | `/`           | The directory to start the search of files that a user wants to attach to work items. The user will be able to navigate though the sub-directories                                                                                                                               |
| `log_file`                                  | str  | No                | `jiratui.log` | The name of the log file to use                                                                                                                                                                                                                                                  |


## Configuring Pre-defined JQL Expressions

To define your own JQL expressions you can use the setting `pre_defined_jql_expressions`. These expressions will be
accessible via the JQL Expression Editor. You can open the editor by going to the JQL Expression input and pressing
`^e`. The setting accepts a dictionary of user-defined IDs whose values are the details of an expression. This includes a
label and, a string with the JQL expression value. The label wil be used as the label of the dropdown selector. Example:

```yaml
pre_defined_jql_expressions:
    1:  {
            "label": "Find work created by John and sort it by created date asc",
            "expression": "creator = 'john' order by created asc"
    }
    2:  {
          "label": "Find work due on 2100-12-31 and for the production environment",
          "expression": "dueDate = '2100-12-31' AND environment = 'production'"
    }
```

## Fetching Only Projects on Startup

When this setting is `True` the application will only load the list of available projects at startup. The list of
status codes, users and work items types will be loaded when the user selects a project. On the other hand, if this is
`False` then the application fill load (i.e. fetch from the API) available status codes, users and work items types in
addition to the available projects. This may make the startup a bit slower.

## Include Jira Server Title in the UI Title

If the setting `tui_title_include_jira_server_title = True` the application will fetch server information from the Jira
API instance and use the server's title or server base URL to build the title of the application. If this is set to
`False` the title will set to the default, or to the value of the `tui_custom_title` setting above; if defined.
