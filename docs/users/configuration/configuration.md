# Configuring JiraTUI

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
`False` the title will set to the default, or to the value of the `tui_custom_title` setting above; if defined.


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

You can control the default sort order for search results using the `search_results_default_order` configuration option. This determines how issues are ordered when you perform a search in JiraTUI.

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
