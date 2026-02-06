# JiraTUI Settings

This page will guide through the process of configuring the application. For a full list of all the configuration
options refer to the [reference documentation](reference.md).

## Choosing a Theme

You can set the theme you want to use for the UI
using [Textual Themes](https://textual.textualize.io/guide/design/). You can do this in a couple of ways.

The default theme used by the app is `textual-dark`. If the theme you provide is not recognized then this theme will be
used as the default.

**Setting the theme in the config file**

You can set the theme using the configuration variable `theme`.

```yaml
theme: 'monokai'
```

**Setting the theme on start up**

You can also provide the name of the theme using the argument `--theme` (`-t`) when launching the application via the
CLI command `jiratui ui`.

```shell
jiratui ui --theme textual-light
```

The application sets the theme based on these rules:

1. `--theme` (`-t`) has priority over `config.theme`
2. If `--theme` (`-t`) and `config.theme` are not defined then the app uses the default
3. If the name of theme you provide is not recognized then the app uses the default

Finally, the app proves a CLI command to list the supported themes.

```shell
jiratui themes

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name             ┃ Usage via CLI                       ┃ Usage via Config                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ textual-dark     │ jiratui ui --theme textual-dark     │ config.theme: "textual-dark"     │
│ textual-light    │ jiratui ui --theme textual-light    │ config.theme: "textual-light"    │
│ nord             │ jiratui ui --theme nord             │ config.theme: "nord"             │
│ gruvbox          │ jiratui ui --theme gruvbox          │ config.theme: "gruvbox"          │
│ catppuccin-mocha │ jiratui ui --theme catppuccin-mocha │ config.theme: "catppuccin-mocha" │
│ textual-ansi     │ jiratui ui --theme textual-ansi     │ config.theme: "textual-ansi"     │
│ dracula          │ jiratui ui --theme dracula          │ config.theme: "dracula"          │
│ tokyo-night      │ jiratui ui --theme tokyo-night      │ config.theme: "tokyo-night"      │
│ monokai          │ jiratui ui --theme monokai          │ config.theme: "monokai"          │
│ flexoki          │ jiratui ui --theme flexoki          │ config.theme: "flexoki"          │
│ catppuccin-latte │ jiratui ui --theme catppuccin-latte │ config.theme: "catppuccin-latte" │
│ solarized-light  │ jiratui ui --theme solarized-light  │ config.theme: "solarized-light"  │
└──────────────────┴─────────────────────────────────────┴──────────────────────────────────┘
```

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
`False` the title will set to the default, or to the value of the `tui_custom_title` setting; if defined.

You can use `tui_custom_title` to set a custom title for the application. If `tui_custom_title` is set to an empty string (`""`), no title will be rendered at all. If `tui_custom_title` is not set, the application will fall back to using `tui_title`.


## Enable Filtering Search Results

JiraTUI allows you to further refine the search results by filtering work items based on their summary. This feature
is controlled by 2 configuration variables.

The variable `search_results_page_filtering_enabled` controls whether this feature is enabled or not. The default is to
be enabled. When this feature is enabled, the user can press `/` while the focus is on the search results table. Doing
so will show an input field that the user can use to refine the search results by filtering items whose summary field
do not match the filtering criteria.

In addition, the variable `search_results_page_filtering_minimum_term_length` defines the minimum number of
characters requires to start filtering results. The default is 3 but can be set to any value >= 1.

## Setting the Default Order for Search Results

You can control the default sort order for search results using the `search_results_default_order` configuration
option. This determines how issues are ordered when you perform a search in JiraTUI.

**Accepted values:**
- `created asc`
- `created desc`
- `priority asc`
- `priority desc`
- `key asc`
- `key desc`

These correspond to the available sort orders in JiraTUI. The value you set must match one of the above exactly.

**Example:**
```yaml
search_results_default_order: 'created desc'
```

You can still change the order interactively in the UI; this setting only controls the initial/default value.

## Setting Git Repositories

Starting with `v1.3.0` JiraTUI allows users to create Git branches directly from the UI. Once you select a work item,
you can press `^g` to open up a dialog to create a new Git branch using the work item's key as the initial value for the
branch.

To support this you need to configure the repositories that the tool can use to create branches. In principle there is
no direct connection between projects and Git repos. A project may use different repos and a repo may be used in
different projects. Because of this you need to configure the Git repos you want to use.

You can do this via the configuration variable `git_repositories`. Using this setting you define repositories
specifying an ID, a name and a path to the repository's `.git` directory.

**Example**:

```yaml
git_repositories:
   1:
      name: 'My Project A'
      path: '/projects/project-a/.git'
   2:
      name: 'My Project B'
      path: '/projects/project-b/.git'
```

Using this configuration JiraTUI will be able to display these repositories and, you will be able to choose the target
repo for creating a new branch.

## Enable Updating Additional Fields

JiraTUI allows the users to update certain types of custom fields and system fields. Currently, the list of custom
fields that can be updated include the following:

- `datepicker`: these fields allow the user to provide a date value, e.g. `2025-12-31`.
- `datetime`: these fields allow the user to provide a date/time value, e.g. `2025-12-31 13:34:55`.
- `float`: these fields allow the user to provide a number, e.g. `12.34`.
- `textfield`: these fields allow the user to provide a simple string as value. No Markdown or ADF is supported by
these fields. Important: this is a restriction of the type as defined by Jira and not a restriction of JraTUI.
- `select`: these fields allow the user to select a single option out of a list of available options.
- `multicheckboxes`: these fields allow the user to select multiple options out of a list of available options.
- `url`: these fields allow the user to provide a URL.

By default, JiraTUI does not allow users to view and update these fields. To enable this feature you can set
the variable `enable_updating_additional_fields: True`.

If, for whatever reason, you want to disable viewing/updating a specific system/custom field enabled by this feature,
you can add the field's ID (or key) to a list of fields to ignore. To do so set the config variable
`update_additional_fields_ignore_ids`.

Example, the following configuration enables the feature to view/update custom fields but disables the feature for the
field with ID `customfield_12345`.

```yaml
enable_updating_additional_fields: True
update_additional_fields_ignore_ids:
  - customfield_12345
```

## Customize the Styling of Components

JiraTUI allows you to customize the styling of some components in the UI. Among these you can set the color the UI uses
to display tasks based on their status, priority or type.

To do this you can use the `styling` setting in the configuration file. Using this you can customize 3 things:

- **Work Item Status**: the color used by the UI to display tasks of a certain status. For this you can use the
configuration variable `work_item_status_colors`. This variable accepts keys that refer to the status of tasks. Each
key can contain the RGB color you want to use to highlight tasks of a certain status. For example, the following
configuration sets the colors of some statuses.

```yaml
styling:
  work_item_status_colors:
    in_progress: blue
    done: '#FFFF00'
```

This configuration tells JiraTUI to use `blue` to highlight tasks whose status is "In Progress" and to use `yellow` to
highlight tasks with status "Done".

```{important}
Colors can be specified using RGB codes (more flexible) or their names. The name of the statuses MUST be written in
lowercase and w/o spaces.
```

```{important}
If a status is not defined under `work_item_status_colors` then JiraTUI chooses the value.
```

- **Work Item Type**: the color used by the UI to display tasks of a certain type. For this you can use the
configuration variable `work_item_type_colors`. This variable accepts keys that refer to the types of tasks. Each
key can contain as value the RGB color you want to use to highlight tasks of a certain type. For example, the following
configuration sets the colors of some types of tasks.

```yaml
styling:
  work_item_type_colors:
    bug: blue
    task: '#FFFF00'
```

This configuration tells JiraTUI to use `blue` to highlight tasks whose type is "Bug" and to use `yellow` to
highlight tasks with type "Task".

```{important}
Colors can be specified using RGB codes (more flexible) or their names. The name of the types MUST be written in
lowercase and w/o spaces.
```

```{important}
If a type is not defined under `work_item_type_colors` then JiraTUI chooses the value.
```

- **Work Item Priority**: the color used by the UI to display tasks of a certain priority. For this you can use the
configuration variable `work_item_priority_colors`. This variable accepts keys that refer to the priorities of
tasks. Each key can contain as value the RGB color you want to use to highlight tasks of a certain priority. For
example, the following configuration sets the colors of some tasks base don their priority.

```yaml
styling:
  work_item_priority_colors:
    high: blue
    highest: '#FFFF00'
```

This configuration tells JiraTUI to use `blue` to highlight tasks whose priority is "High" and to use `yellow` to
highlight tasks with priority "Highest".

```{important}
Colors can be specified using RGB codes (more flexible) or their names. The name of the priorities MUST be written in
lowercase and w/o spaces.
```

```{important}
If a priority is not defined under `work_item_priority_colors` then JiraTUI chooses the value.
```

## Searching Work Items in Active Sprint on Startup

You can instruct JiraTUI to start with the checkbox `Active Sprint` checked. This is useful if you want to always
search tasks in the current sprints w/o having to check the box manually when needed. The default is `False` which
means the checkbox will be unchecked.
