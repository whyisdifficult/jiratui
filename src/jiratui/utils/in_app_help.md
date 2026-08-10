# JiraTUI Documentation

This document guides you through some of the most important aspects of using the tool. If you need more help on how to
configure the tool or more details on how the tool works you can refer to the official docs at
[https://jiratui.readthedocs.io/en/latest/index.html](https://jiratui.readthedocs.io/en/latest/index.html)

# Navigating the UI

Starting with `v1.3.0`, JiraTUI allows you to choose the style of keybindings you want to use. You can do so by setting
the variable `key_bindings_style` in the configuration file. The default value is `legacy`. The other option is
`standard`.

The `legacy` style uses the keybindings implemented in the app since the beginning. The `standard` style uses
keybindings that are usually found in other terminal-based applications. The following tables describe them and their
context.

## Standard Style

| Keys      | Description                                            | Context                                                                 |
|-----------|--------------------------------------------------------|-------------------------------------------------------------------------|
| `tab`     | Focus next element                                     |         |
| `^q`      | Closes the app                                         |         |
| `q`       | Closes the app                                         |         |
| `f1`      | Open the help                                          | Main Screen                                                             |
| `f2`      | View details of your Jira server                       | Main Screen                                                             |
| `f3`      | View the configuration file                            | Main Screen                                                             |
| `f4`      | Shows the recent history                               | Main Screen                                                             |
| `f5`      | View items related to the currently selected work item | Main Screen                                                             |
| `f6`      | Creates a Git branch for a work item                   | Main Screen                                                             |
| `alt+p`   | Focuses the project dropdown                           | Main Screen                                                             |
| `alt+t`   | Focuses the work item types dropdown                   | Main Screen                                                             |
| `alt+s`   | Focuses the work item statuses dropdown                | Main Screen                                                             |
| `alt+a`   | Focuses the assignee dropdown                          | Main Screen                                                             |
| `alt+k`   | Focuses the work item key search input                 | Main Screen                                                             |
| `alt+f`   | Focuses the created-from search input                  | Main Screen                                                             |
| `alt+u`   | Focuses the created-until search input                 | Main Screen                                                             |
| `alt+o`   | Focuses the sorting search input                       | Main Screen                                                             |
| `alt+v`   | Focuses the active-sprint search input                 | Main Screen                                                             |
| `alt+j`   | Focuses the JQL search input                           | Main Screen                                                             |
| `/`       | Search work items                                      | Main Screen                                                             |
| `^f`      | Perform a full-text search of work items               | Main Screen                                                             |
| `1`       | Focuses the search results table                       | Main Screen                                                             |
| `2`       | Focuses the work item information tab                  | Main Screen                                                             |
| `3`       | Focuses the work item details tab                      | Main Screen                                                             |
| `4`       | Focuses the work item comments tab                     | Main Screen                                                             |
| `5`       | Focuses the related work items tab                     | Main Screen                                                             |
| `6`       | Focuses the attachments tab                            | Main Screen                                                             |
| `7`       | Focuses the web links tab                              | Main Screen                                                             |
| `8`       | Focuses the work item subtasks tab                     | Main Screen                                                             |
| `^n`      | Creates a new work item                                | Main Screen                                                             |
| `y`       | Copy the work item key                                 | Main Screen                                                             |
| `^c`      | Copy the work item URL                                 | Main Screen                                                             |
| `f`       | Filter work items in the search results table          | Search Results Table                                                    |
| `[`       | Go to the previous page                                | Search Results Table                                                    |
| `]`       | Go to the next page                                    | Search Results Table                                                    |
| `x`       | Deletes a resource                                     | Search Results Table                                                    |
| `enter`   | Select the item under the cursor                       | Search results table                                                    |
| `up`, `k` | Move up                                                | Search results table                                                    |
| `down`, `j` | Move down                                              | Search results table                                                    |
| `right`, `l` | Move to the right                                      | Search results table                                                    |
| `left`, `h` | Move to the left                                       | Search results table                                                    |
| `pageup`, `^b` | Move 1 page up                                         | Search results table                                                    |
| `pagedown` | Move 1 page down                                       | Search results table                                                    |
| `^home`   | Scroll to the top                                      | Search results table                                                    |
| `^end`    | Scroll to the bottom                                   | Search results table                                                    |
| `home`    | Scroll to the beginning                                | Search results table                                                    |
| `end`     | Scroll to the end                                      | Search results table                                                    |
| `a`       | Add a comment                                          | Comments Tab                                                            |
| `x`       | Delete a comment                                       | Comments Tab                                                            |
| `a`       | Create a link between work items                       | Links Tab                                                               |
| `x`       | Delete a link between work items                       | Links Tab                                                               |
| `a`       | Add a web link to a work item                          | Links Tab                                                               |
| `x`       | Delete a web link from a work item                     | Links Tab                                                               |
| `a`       | Add a subtask to a work item                           | Subtasks Tab                                                            |
| `v`       | View details of a work item                            | Related Tab, Subtasks Tab                                               |
| `e`       | Edit the (text) content of a resource                  | Info Tab                                                                |
| `v`       | View the text content of a resource                    | Info Tab                                                                |
| `c`       | Copy the text content of a resource                    | Info Tab                                                                |
| `^e`      | Edit JQL expressions                                   | JQL Search Filter                                                       |
| `w`       | View the worklog of a work item                        | Details Tab                                                             |
| `^s`       | Save the text content of a resource                    | Details Tab, Create/Update Screens                                      |
| `l`       | Log work done for a work item                          | Worklog Screen                                                          |
| `x`       | Delete worklog entry                                   | Worklog Screen                                                          |
| `e`       | Edit worklog entry                                     | Worklog Screen                                                          |
| `*`       | Flag a work item                                       | Details Screen                                                          |
| `a`       | Attach a file to a work item                           | Attachments Tab                                                         |
| `o`       | Open attachment                                        | Attachments Tab                                                         |
| `x`       | Delete attachment                                      | Attachments Tab                                                         |
| `x`       | Empty recent history                                   | Recent History Screen                                                   |
| `o`       | Open resource in the browser                           | Search results table, Worklog, Recent history screen, Quick view screen |

## Legacy Style

| Keys | Description                                              | Context |
|-----|----------------------------------------------------------|---------|
| `tab` | Focus next element                                       |         |
| `^q` | Closes the app                                           |         |
| `f1`, `^?`, `^+shift+\` | Open the help                                            |         |
| `f2` | View details of your Jira server                         |         |
| `f3` | View the configuration file                              |         |
| `p` | Focuses the project dropdown                             |         |
| `t` | Focuses the work item types dropdown                     |         |
| `s` | Focuses the work item statuses dropdown                  |         |
| `a` | Focuses the assignee dropdown                            |         |
| `k` | Focuses the work item key search input                   |         |
| `f` | Focuses the created-from search input                    |         |
| `u` | Focuses the created-until search input                   |         |
| `o` | Focuses the sorting search input                         |         |
| `v` | Focuses the active-sprint search input                   |         |
| `j` | Focuses the JQL search input                             |         |
| `^r` | Search work items                                        |         |
| `/` | Perform a full-text search of work items                 |         |
| `1` | Focuses the search results table                         |         |
| `2` | Focuses the work item information tab                    |         |
| `3` | Focuses the work item details tab                        |         |
| `4` | Focuses the work item comments tab                       |         |
| `5` | Focuses the related work items tab                       |         |
| `6` | Focuses the attachments tab                              |         |
| `7` | Focuses the web links tab                                |         |
| `8` | Focuses the work item subtasks tab                       |         |
| `^n` | Creates a new work item                                  |         |
| `f7` | Shows the recent history                                 |         |
| `^k` | Copy the work item key                                   |         |
| `^j` | Copy the work item URL                                   |         |
| `^g` | Creates a Git branch for a work item                     |         |
| `.` | Filter work items in the search results table            |         |
| `alt+left` | Go to the previous page                                  |         |
| `alt+right` | Go to the next page                                      |         |
| `d` | Deletes a resource                                       |         |
| `f6` | View items related to the selected work item             |         |
| `enter` | Select the item under the cursor                         |         |
| `up` | Move up                                                  |         |
| `down` | Move down                                                |         |
| `right` | Move to the right                                        |         |
| `left` | Move to the left                                         |         |
| `pageup` | Move 1 page up                                           |         |
| `pagedown` | Move 1 page down                                         |         |
| `^home` | Scroll to the top                                        |         |
| `^end` | Scroll to the bottom                                     |         |
| `home` | Scroll to the beginning                                  |         |
| `end` | Scroll to the end                                        |         |
| `n` | Add a comment                                            |         |
| `d` | Delete a comment                                         |         |
| `n` | Create a link between work items                         |         |
| `v` | View details of a work item                              |         |
| `d` | Delete a link between work items                         |         |
| `n` | Add a web link to a work item                            |         |
| `d` | Delete a web link from a work item                       |         |
| `n` | Add a subtask to a work item                             |         |
| `^e` | Edit the (text) content of a resource                    |         |
| `^l` | View the worklog of a work item                          |         |
| `^t` | [DEPRECATED] Log work for a work item. Use `^l` instead. |         |
| `^f` | Flag a work item                                         |         |
| `n` | Log work done for a work item                            |         |
| `^o` | Open resource in the browser                             |         |
| `d` | Delete worklog entry                                     |         |
| `^e` | Edit worklog entry                                       |         |
| `d` | Empty recent history                                     |         |
| `v` | View the text content of a resource                      |         |
| `c` | Copy the text content of a resource                      |         |
| `^s` | Save the text content of a resource                      |         |
| `^e` | Edit JQL expressions                                     |         |
| `^u`, `n` | Attach a file to a work item                             |         |
| `^o` | Open attachment                                          |         |
| `d` | Delete attachment                                        |         |


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

You can select a Jira user to act as an assignee and search work items assigned to that user. To do that you simply
type in the name in the search box "Assignee" at the top of the app. Users are filtered by their email address and
their display name. If you select a project from the "Projects" dropdown then users will be filtered by the project's
key in addition to being filtered by their name/email address.

# Creating Git Branches

If you want to create a Git branch for a work item you can do so by selecting the work item int he search results and
then pressing `^g`. This will open a pop-up screen and will allow you to specify the target repository and the name of
the branch. The list of available repositories is controlled by the configuration variable `git_repositories`.

# Creating Work Items

To create a work item you can press `ctrl+n`. This will open up a modal screen with a form to provide the necessary
fields to create the work item. Fields marked with `(*)` are required. If the item is created successfully a message
will pop up in the app indicating the work item key.

The form includes a fixed set of fields and, a set of fields that are dynamically created depending on the project and
type of work item that you want to create. These fields are always present in the form:

- Project
- Issue Type: this depends on the selected project
- Reporter
- Assignee
- Parent Key: this is only relevant for sub-tasks
- Summary
- Description: If your Jira instance runs on the cloud and uses API v3 then it supports ADF. In this case you can
write your description in CommonMark. If you Jira instance runs on your DC or uses API v2 then ADF is not supported
and the text you provide will be treated as plain text.

When you select a type of issue the form will be updated to include additional fields. These are created dynamically
based on the create-metadata associated to the type of issue you want to create. These fields are controlled by 2
configuration variables:

- `enable_creating_additional_fields`: this controls whether the form should include dynamic fields or not.
- `create_additional_fields_ignore_ids`: this controls which dynamic fields to skip. You can specify a list of field ids
to skip.

*Tip*: when you hover over a field's input widget a tooltip will give you the id of the field.

# Updating Work Items

The "Details" tab on the right-hand side shows the details of the currently selected work item. The tab displays a form
with the fields that are supported by the app. Some of these fields can be updated. The list of fields that can be
updated include the following:

- Summary
- Assignee
- Status
- Priority
- Due Date
- Labels
- Parent
- Components

In addition to the fields above the application supports updating (some) custom field types and some system field
types. Currently, the list of custom fields that can be updated include the following:

- `datepicker`: these fields allow the user to provide a date value, e.g. `2025-12-31`.
- `datetime`: these fields allow the user to provide a date/time value, e.g. `2025-12-31 13:34:55`.
- `float`: these fields allow the user to provide a number, e.g. `12.34`.
- `textfield`: these fields allow the user to provide a simple string as value. No Markdown or ADF is supported by
these fields. **Important**: this is a restriction of the type as defined by Jira and not a restriction of JraTUI.
- `select`: these fields allow the user to select a single option out of a list of available options.
- `multicheckboxes`: these fields allow the user to select multiple options out of a list of available options.
- `url`: these fields allow the user to provide a URL.

By default, JiraTUI does not allow users to view and update the fields in the above. To enable this feature you can set
the variable `enable_updating_additional_fields: True` in the config file. For more details refer to
[Enable Updating Additional Fields](https://jiratui.readthedocs.io/en/latest/users/configuration/configuration.html#enable-updating-additional-fields)
in the official documentation page.

In order to update a field simply focus on it, change its value and then press `^s` to save the changes.

Some of the fields require a modal to pop up to allow the user to select values for the field. These fields include a
tip that reads "press enter to update". This is the case for custom fields of type `multicheckboxes`.

**Updating the parent of an issue**

Jira arranges the type sof issues into a hierarchy. This hierarchy is used to determine whether an issue can have
another issue as a parent. For example, an Epic can not have a parent issue. Issues of type Story, Task, Bug and
Subtask do accept parents.

Jiratui disables the parent field of an issue when its type does not allow parents to be set; e.g. for Epics.

**Updating priorities**

Once an issue has a priority set up it can not be unset.

**Updating the Components of a Work Item**

If you Jira project configures a `components` field for the issues in the project then the application will allow you
to view and update the components associated to a work item. If you do not see the input field to view and update this
field then the probable reason is that your Jira project does not support this field.

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
attached file you want to delete and then press `d`. For some files the application provides a shortcut to view the
content of the file directly in the terminal; this includes some types of images. When the user selects the attachment
and presses `enter` (or clicks on the attachment row) the app will attempt to download the file display its content in
the terminal. In addition, after selecting/highlighting an attachment the user can press `^o` to open the file in the
browser.

**Important**: Uploading large files may cause the UI to be unresponsive temporarily. This will depend on the size of
the file.

**Important**: In order to open attachments in the default browser the user **MUST** be logged into the browser.

**Warning**: The application imposes a maximum file size of 10MB.

## Web Links

This will display a list of URLs associated to the selected work item. files attached to the selected work item.

To add a new link simply press `n` and provide the details in the pop-up that opens. To delete a link simply focus on
the title of the collapsible whose link you want to delete and then press `d`.

## Subtasks

This will display a list of work items that are a sub task of the selected work item. A work item `A` is a subtask of
another work item `B` if the parent of `A` is `B`.

## Worklogs

The "Details" tab also allows you to log work for a given work item. To do so you can press `^l` to open a pop-up screen
that will show you the time tracking information of the selected item together with the log entries. In this new screen
you can do the following:

- press `n` to add a new entry.
- press `tab` to select an entry and then
  - press `^e` to update it.
  - press `d` to delete it.
  - press `^o` to open the entry in the browser.

## Flagging Work Items

You can add/remove a flag to a work item by pressing `^f` while in the details tab. When you add a flag to an item you
can add an optional message to let your team know why the task is (not) flagged.

# Deleting Work Items

To delete a work item you can select an item from the search results pane on the left and then click `d`. This will
open a modal screen that will let you confirm the deletion.

**Important**: if an item has subtasks all of them will also be deleted.


# View Related Items

After you perform a search and select an item from the search results you can view the items related to the selected
work item. To do this press `f6`.

Pressing `f6` will open a modal screen that will list all the related items. These can be subtasks, a parent task, or
tasks related via another relationship, e.g. "causes".

In the new screen you can press `tab` to move around to different items. After highlighting an item from the tables you
can do the following:

- press `^o` to open the item in the browser.
- press `^k` to copy the item's key to the clipboard.
- press `^j` to copy the item's URL to the clipboard.

In addition to this, if you select an item from the tables by pressing `enter` on it JiraTUI will close the screen and
fetch the details of the select item. This gives you a quick way to navigate through related items.

# View Recent Items

Every time you select an item from the search results by pressing `enter` JiraTUI will remember the item in the current
application's session. The same happens when you add or update an item. To view the list of recently added/updated/viewed
items you can press `f7`.

Doing so will open a modal screen that will display a list of items.

In the new screen you can press `tab` to move around to different items. After highlighting an item from the tables you
can do the following:

- press `^o` to open the item in the browser.
- press `^k` to copy the item's key to the clipboard.
- press `^j` to copy the item's URL to the clipboard.

In addition to this, if you select an item from the tables by pressing `enter` on it JiraTUI will close the screen and
fetch the details of the select item. This gives you a quick way to navigate through related items.

Last, you can empty the list of recent items by pressing `d`.
