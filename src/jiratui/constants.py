ISSUE_SEARCH_DEFAULT_MAX_RESULTS = 30
ISSUE_SEARCH_DEFAULT_DAYS_INTERVAL = 15
"""The number of days to search for work items when the "created date" limit is not specified."""
ATTACHMENT_MAXIMUM_FILE_SIZE_IN_BYTES = 10485760  # 10MB
"""The maximum size of files that can be attached to work items. This is a restriction imposed by this tool and not by
Jira."""
LOGGER_NAME = 'jiratui'
LOG_FILE_FILE_NAME = 'jiratui.log'
DEFAULT_JIRA_API_VERSION = 3
FULL_TEXT_SEARCH_DEFAULT_MINIMUM_TERM_LENGTH = 3

APPLICATION_HELP = """\
# JiraTUI Documentation

This document guides you through some of the most important aspects of using the tool. If you need more help on how to
configure the tool or more details on how the tool works you can refer to the official docs at
[https://jiratui.readthedocs.io/en/latest/index.html](https://jiratui.readthedocs.io/en/latest/index.html)

# Navigating the UI

You can move around in the UI with the `tab` key or, by using your mouse. However, if you want to move faster you can
jump to some of the components by pressing a single key. Some components in UI indicate between parenthesis the key that
you can use to jump to them. For example, to quickly jump to the Project dropdown you can simply click `p`. If the focus
is currently on a component you need to press `esc` to move the focus out and then the key you desired. The following
table summaries the hot-keys and the component they activate.

| Key | Component                                         |
|-----|---------------------------------------------------|
| `p` | Activates the Project dropdown                    |
| `t` | Activates the Issue Type dropdown                 |
| `s` | Activates the Status dropdown                     |
| `a` | Activates the Assignee dropdown                   |
| `k` | Activates the Work Item Key input                 |
| `f` | Activates the Created From input                  |
| `u` | Activates the Created Until input                 |
| `o` | Activates the Sort dropdown                       |
| `v` | Activates the Active Sprint checkbox              |
| `j` | Activates the JQL Query input                     |
| `1` | Activates the Work Items search result table/pane |
| `3` | Activates the Details tab                         |
| `4` | Activates the Comments tab                        |
| `5` | Activates the Related tab                         |
| `6` | Activates the Attachments tab                     |
| `7` | Activates the Links tab                           |
| `8` | Activates the Subtasks tab                        |

When you select a work item from the Work Items search results pane and click `enter` the information of the work item
is loaded into the tabs on the right-hand side. Depending on the tab that is active certain hot-keys are enabled:

| Key         | Active Tab/Component | Action                                                                     |
|-------------|----------------------|----------------------------------------------------------------------------|
| `ctrl+s`    | Details              | Saves change to a work item                                                |
| `ctrl+l`    | Details              | View the work log                                                          |
| `n`         | Comments             | Add a new comment to the work item                                         |
| `n`         | Related              | Add a new related item to the work item                                    |
| `n`         | Related              | Add a new related item to the work item                                    |
| `ctrl+u`    | Attachments          | Attach file to the work item                                               |
| `ctrl+u`    | Attachments          | Attach file to the work item                                               |
| `n`         | Links                | Link item to the work item                                                 |
| `n`         | Links                | Link item to the work item                                                 |
| `ctrl+n`    | Subtasks             | Create a new subtask of the work item                                      |
| `.`         | Search Results       | Enables filtering of results in the results table                          |
| `alt+right` | Search Results       | Retrieves the next page of results                                         |
| `alt+left`  | Search Results       | Retrieves the previous page of results. This is only enabled when page > 1 |
| `ctrl+e`    | JQL Query field      | Opens the JQL Query Editor                                                 |

Besides the hot-keys above the following are always available.

| Key      | Action                                                                 |
|----------|------------------------------------------------------------------------|
| `ctrl+r` | Searches work items (this is the same as clicking the "Search" button) |
| `/`      | Enables full-text search                                               |
| `ctrl+n` | Creates a new work item                                                |
| `f1`     | Shows this help                                                        |
| `f2`     | Shows server information                                               |
| `f3`     | Shows the currently loaded settings                                    |

All these bindings above are always displayed at the bottom of the app depending on the component you are focus on.

# Searching Work Items

JiraTUI supports a few ways to search work items.

## Search using filters

You can use the filters at the top of the app to setup the criteria you want to use for searching work items. Once
you select the desired values simply click `ctrl+r` or, click the `Search` button.

The maximum number of results that the app will retrieve and show is controlled by the setting
`search_results_per_page`. The default value is 30. If the search criteria yields work items the app will display them
in the Work Items pane on the left.

### Search by Work Item Key

This expects a case-sensitive string. If defined, this has precedence over all the other search criteria.

### Search by Work Item Type

Search work items based on their type. If a project is selected then this list will contain the type of work items
supported by the project. If no project is selected then this list will contain all the types of work items available
in the known projects.

**Important**: this list may contain types with duplicated names when there is no project selected. The id of these
types will be different though.

### Search by Status

Search work items based on their status. If a project is selected then this list will contain the statuses supported by
the work types in the project. If no project is selected then this list will contain all possible statuses.

### Search by Assignee

Search work items based on their assignee. If a project is selected then this list will contain the active users that
can have work items assigned in the project. If no project is selected then this list will contain all available
(active) users.

### Search by Created From Date

If defined, only work items that were created after this date (inclusive) will be fetched.

If no `Created From` and `Created Until` search criteria are defined then the tool will fetch work items created
within the last 15 days. The number of days can be specified by the configuration variable
`search_issues_default_day_interval`.

### Search by Created Until Date

If defined, only work items that were created until this date (inclusive) will be fetched.

If no `Created From` and `Created Until` search criteria are defined then the tool will fetch work items created
within the last 15 days. The number of days can be specified by the configuration variable
`search_issues_default_day_interval`

### Search by Active Sprint

When this checkbox is checked the application will filter work items that correspond to the currently active
sprint.

## Searching using full-text search

In addition to searching using the filters above, JiraTUI allows you to search items using full-text
search. This type of search has 2 modes: standard and advanced.

- **Standard Full-text Search**: this modes searches items using the items' summary and description fields. This uses
queries of the form `summary ~ "search term" OR description ~ "search term"`.

- **Advanced Full-text Search**: in addition to searching items using the items' summary and description fields, this
modes also searches items by using any text-based field. This includes comments. This uses
queries of the form `text ~ "search term".

If you want/need to disable advanced full-text search you can do so with the setting
`enable_advanced_full_text_search`. Also, the setting `full_text_search_minimum_term_length` controls the minimum
length of the search term to activate the search. Independently of the value you enter for this variable JiraTUI imposes
a minimum of 3 characters.

For more details on full-text search in Jira refer to
https://support.atlassian.com/jira-software-cloud/docs/jql-fields/#Text) and
https://support.atlassian.com/jira-software-cloud/docs/search-for-work-items-using-the-text-field/.

**Important**: Full-text search is only available when you connect to the Jira Cloud Platform. This feature is not
available when you connect to Jira Data Center (aka. server, on-premises).

To activate full-text search press `/`. Enter the search term in the pop-up and hit `enter`.

## Searching Using JQL Expressions

Another way to search work items in JiraTUI is by crafting your own [JQL query](). You can do so using the JQL Query
input field. In addition, you can also define your own JQL query expressions and save them in the config file using the
setting `pre_defined_jql_expressions`. This is a YAML dictionary of expressions. When you focus on the JQL Query input
field (`j`) and press `ctrl+e` the JQL Editor opens. Here you can write a complex query or, choose one from the
dropdown.

**Examples**

- Search work items assigned to John Smith

```python
assignee = "John Smith"
```

or searching by the user's email address:

```python
assignee = "john@smith.com"
```

# Filtering results

Search results can be filtered as well. In order to do this simply focus on the results table by pressing `1` and then
press `.`. This opens up an input field where you can enter the term you want to use to filter the results further.
Items are filtered by their `summary` field. Keep in mind that the filtering only applies to the current page.

This feature is controlled by the setting `search_results_page_filtering_enabled`. The minimum length of the search
term is controlled by the setting `search_results_page_filtering_minimum_term_length`; the default is 3.

**Tip**: pressing `escape` hides the search box.

# Choosing the Values of the Filters

The 4 filters at the top are linked together. When you choose a project from the dropdown the types of issues,
applicable status codes and the list of users get automatically updated. This is because the values of these 3 filters
may vary with each project.

## Projects List

The list of projects depends on the permissions of the logged-in user. For a project to appear on this list
one of these conditions must be satisfied:

- The user Jira account must have the [Browse Projects project permission](https://confluence.atlassian.com/x/yodKLg)
for the project.
- The user Jira account must have the [Administer Projects project permission](https://confluence.atlassian.com/x/yodKLg)
for the project.
- The user Jira account must have the [Administer Jira global permission](https://confluence.atlassian.com/x/x4dKLg).

By default JiraTUI will retrieve all available projects. However, if you set the config variable
`default_project_key_or_id` with a case-sensitive project key then the app will only fetch and load that project. If
no project is found or the user does not have permissions to browse projects then this list will be empty.

## Issues Types List

If you select a project then JiraTUI will retrieve all the applicable issue types for the selected project. If no
project is selected then the list of issue types will include all known issue types. Keep in mind that in this case the
dropdown may contain types with the same name; because they belong to different projects.

## Issue Status Codes

If you select a project then JiraTUI will retrieve all the applicable statis codes applicable to the issue types of the
selected project. If no project is selected then the list of statuses will include all known status codes. Keep in mind
that in this case the dropdown may contain statuses with the same name; because they belong to different projects.

## List of Users

If you select a project then JiraTUI will retrieve all the users that can be assigned issues in the given
project. Otherwise the app will attempt to find all the users that belong to the group ID defined in
`jira_user_group_id`.

**Important**: fetching users by group id is only supported in the Jira Cloud Platform.

# Creating Work Items

To create a work item you can press `ctrl+n`. This will open up a modal screen with a form to provide the necessary
fields to create the work item. Fields marked with `(*)` are required. If the item is created successfully a message
will pop up in the app indicating the work item key.

# Updating Work Items

This contains the details of the selected work item. Some of these details can be edited/updated. Currently, the
fields that can be updated are:

- Summary
- Assignee
- Status
- Priority
- Due Date
- Labels
- Parent

To edit a field simply focus on it, change its value and then press `^s` to save the changes.

**Updating the parent of an issue**

Jira arranges the type sof issues into a hierarchy. This hierarchy is used to determine whether an issue can have
another issue as a parent. For example, an Epic can not have a parent issue. Issues of type Story, Task, Bug and
Subtask do accept parents.

Jiratui disables the parent field of an issue when its type does not allow parents to be set; e.g. for Epics.

**Updating priorities**

Once an issue has a priority set up it can not be unset.

## Comments

This contains the comments associated to the selected work item. Comments can be deleted by focusing on them and then
pressing `d`. Comments can be added by pressing `n`.

## Related Work Items

This will display a summary of all the work items related to the item currently selected.

Pressing `n` allows the user to add new related work items while focusing on a related item and then pressing `d` will
delete the item.

To view the details of a related item simply focus on the item and then press `v`.

## Attachments

This will display a list of files attached to the selected work item.

To upload a file press `^u` and provide the details in the pop-up that opens. To delete an attachment focus on the
attached file you want to delete and then press `d`.

**Important**: Uploading large files may cause the UI to be unresponsive temporarily. This will depend on the size of
the file.

**Warning**: The application imposes a maximum file size of 10MB.

## Web Links

This will display a list of URLs associated to the selected work item. files attached to the selected work item.

To add a new link simply press `n` and provide the details in the pop-up that opens. To delete a link simply focus on
the title of the collapsible whose link you want to delete and then press `d`.

## Subtasks

This will display a list of work items that are a sub task of the selected work item. A work item `A` is a subtask of
another work item `B` if the parent of `A` is `B`.

"""
