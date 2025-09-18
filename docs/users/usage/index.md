# Usage

## Launching the UI

Once you have provided the necessary settings, you can run the application's UI with the following command:

```shell
$ jiratui ui
```

If you are using a custom config file, run:

```shell
$ JIRA_TUI_CONFIG_FILE=my-file.yaml jiratui ui
```

If everything works fine you should see the screen shown in the image below

```{figure} /_static/assets/images/jiratui_home.png
:align: center

The initial screen of the application
```

### Passing Optional Arguments to the UI

`jiratui ui` supports optional arguments that you can use to set options in the UI upon start up. You can view the list
of supported arguments with the following command:

```shell
$ jiratui ui --help
Usage: jiratui ui [OPTIONS]

  Launches the JiraTUI application.

Options:
  -p, --project-key TEXT          A case-sensitive Jira project key.
  -w, --work-item-key TEXT        A case-sensitive key of a work item.
  -u, --assignee-account-id TEXT  A Jira user account ID. Typically this would be your Jira account ID so user-related
                                  dropdowns can pre-select your user
  -j, --jql-expression-id TEXT    The ID of a JQL expression as defined in the config.
  -t, --theme TEXT                The name of the theme to use.
```

#### Selecting a Theme

JiraTUI allows you to set the theme of the UI when you launch it. Currently, the application supports the themes
pre-defined by the [underlying framework](https://textual.textualize.io/guide/design/#themes).

You can list the supported themes with the `jiratui themes` command:

```shell
$ jiratui themes

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

The default theme is `textual-dark`.

To start the UI with a different theme you can pass the name of the theme to the `ui` command. For example, the
following command will start the UI with the theme `dracula`.

```shell
$ jiratui ui --theme dracula
```

For more details refer to [Choosing a Theme](../configuration/configuration.md#choosing-a-theme)

#### Select a Jira Project on Start Up

If you want your app to pre-select a project in the projects dropdown you can pass the project key with the argument
`--project-key`. If the project exists the app will pre-select it.

```{tip}
You can configure the app to always do this by setting the variable `default_project_key_or_id` in the config
file. That way you do not need to pass this argument when you start the app.
```

```shell
$ jiratui ui --project-key PROJECT-1
```

#### Select a Jira User on Start Up

If you want your app to pre-select a/your Jira user in the assignees dropdown you can pass the user account ID with
the argument `--assignee-account-id`. If the user exists the app will pre-select it.

```{tip}
You can configure the app to always do this by setting the variable `jira_account_id` in the config
file. That way you do not need to pass this argument when you start the app.
```

```shell
$ jiratui ui --assignee-account-id 12345-67890
```

#### Select a Jira Work Item on Start Up

If you want your app to pre-select a Jira issue in the "work item key" field you can pass the work item key with
the argument `--work-item-key`.

```shell
$ jiratui ui --work-item-key ISSUE-1
```

#### Select a JIra JQL Expression on Start Up

If you defined JQL expressions via the config variable `pre_defined_jql_expressions` and you would like the app to
use a specific expression to search work items when no other criteria is selected then you can pass the argument
`--jql-expression-id` with the ID of the expression.

```{tip}
You can configure the app to always do this by setting the variable `jql_expression_id_for_work_items_search` in the
config file. That way you do not need to pass this argument when you start the app.
```

```shell
$ jiratui ui --jql-expression-id 1
```

## CLI Interface

In addition to the `ui` command, the CLI tool offers several commands to help you manage issues, comments, and
users.

```{note}
The CLI tool offers a simples interface for interacting with Jira when compared to the UI app. It's only meant to be
used as a quick tool for some common tasks, for example, transitioning items from one staus to another. For a comore
complete experience the UI is recommended.
```

### Searching for Issues

The CLI has a command to search work items by different criteria.

```shell
$ jiratui issues search --help
Usage: jiratui issues search [OPTIONS]

  Search work items.

Options:
  -p, --project-key TEXT          A case-sensitive key that identifies a project.
  -k, --key TEXT                  A case-sensitive key that identifies a work item.
  -u, --assignee-account-id TEXT  The account ID of a user to filter work items.
  -l, --limit INTEGER             The number of work items to return. Default is 10 items within the last 15 days.
  --created-from [%Y-%m-%d]       Searches issues created from this date forward (inclusive). Expects YYYY-MM-DD
  --created-until [%Y-%m-%d]      Searches issues created until this date (inclusive). Expects YYYY-MM-DD
```

To search for work items in the project `SCRUM`, use the issues search command and pass the `--project-key` argument
with the (case-sensitive) project key.

**Example**: searching for issues of the project `SCRUM`

```shell
$ jiratui issues search --project-key SCRUM

| Key     | Type | Created          | Status (ID)   | Reporter          | Assignee          | Summary                                    |
|---------|------|------------------|---------------|-------------------|-------------------|--------------------------------------------|
| SCRUM-1 | Bug  | 2025-07-31 15:55 | To Do (10000) | lisa@simpson.com  | bart@simpson.com  | Write 100 times "I will be a good student" |
| SCRUM-2 | Task | 2025-06-30 15:56 | To Do (10000) | homer@simpson.com | homer@simpson.com | Eat donuts                                 |
```

To search for a specific work item, use the issues search command with the `--key` (or `-k`) argument and the (case-sensitive)
issue key.

**Example**: searching for the issue with key `SCRUM-1`

```shell
$ jiratui issues search --key SCRUM-1

| Key     | Type | Created          | Status (ID)   | Reporter          | Assignee          | Summary                                    |
|---------|------|------------------|---------------|-------------------|-------------------|--------------------------------------------|
| SCRUM-1 | Bug  | 2025-07-31 15:55 | To Do (10000) | lisa@simpson.com  | bart@simpson.com  | Write 100 times "I will be a good student" |
```

The command allows you to limit the number of items you search. Simply pass the `-l` argument with the number of items
you want to retrieve. In addition, you can filter items based on the creation date with the arguments `--created-from`
and `--created-until`.

### Show Metadata

The tool also provides a command to show metadata associated to a work item. This is useful when you need to update a
work item; for example if you want to transition the state of the item and you need to know the ID of the state.

```shell
$ jiratui issues metadata SCRUM-1

Valid work types for work item: SCRUM-1

| ID     | Name | Current?  | Description                                 |
|--------|------|-----------|---------------------------------------------|
| 1      | Bug  | Yes       | Tasks track small, distinct pieces of work. |
| 2      | Task |           | Bugs track problems or errors.              |

Valid priority IDs for work item: SCRUM-1

| ID     | Name | Current?  | Example   |
|--------|------|-----------|-----------|
| 1      | High  |          |           |

Valid status transitions for work item: SCRUM-1

| Transition ID  | Status ID | Status Name  | Current?   | Example                                      |
|----------------|-----------|--------------|------------|----------------------------------------------|
| 1              | 5         | To Do        | Yes        | <CLI> issues update <ITEM-KEY> --status-id 5 |
| 2              | 6         | Done         |            | <CLI> issues update <ITEM-KEY> --status-id 6 |
```

### Update Work Items

The `issues metadata` command is useful because you can get the data necessary for updating work items.

The command `issues update` can be used to update (some of the) fields of a work item. The (sub)command requires you
to provide the case-sensitive key of the work item you want to update.

```shell
$ jiratui issues update --help

Usage: jiratui issues update [OPTIONS] WORK_ITEM_KEY

  Updates (some) fields of the work item identified by WORK_ITEM_KEY.

  WORK_ITEM_KEY is the case-sensitive key that identifies the work item we want to update.

Options:
  -s, --summary TEXT              Text to set as the summary (aka. title) of the work item.
  -u, --assignee-account-id TEXT  The account ID of the user to whom the work item will be assigned. Pass -u "" or -u null to unassign the work item.
  -d, --due-date [%Y-%m-%d]       Update the due date of an issue. Expects YYYY-MM-DD
  --meta                          Shows metadata for an issue. This is useful for updates.
  -t, --status-id INTEGER         The ID of the status to set for the work item. Use --meta for more details.
  -p, --priority-id INTEGER       The ID of the priority to set for the work item. Use --meta for more details.
```

#### Update Summary

To update the summary of a work item you can pass the `-s` argument with the summary you want to set. For example,

```shell
$ jiratui issues update SCRUM-1 -s "Update the payment method"
```

#### Update Due Date

To update the due date of a work item you can pass the `-d` argument with the date value you want to set. For example,

```shell
$ jiratui issues update SCRUM-1 -d 2025-12-31
```

#### Update Assignee

To update the assignee of a work item you can pass the `-u` argument with the ID of the user's account you want to
set. For example,

```shell
$ jiratui issues update SCRUM-1 -u 12345
```

```{tip}
If you do not know the ID of a user you can use the [search users command](#search-users) to find out.
```

If you want to unassign an issue yu can do so by passing an empty string to the argument `-u` or, `-u null`.

```shell
$ jiratui issues update SCRUM-1 -u ""
```

#### Update Status

To update the status of a work item you can pass the `-t` argument with the ID of the status you want to set. For
example,

```shell
$ jiratui issues update SCRUM-1 -t 6
```

This will allow you to transition the work item with key `SCRUM-1` from the current status to the status Done. See the
[metadata command](index.md#show-metadata) above for the context.

#### Update Priority

To update the priority of a work item you can pass the `-p` argument with the ID of the priority you want to set. For
example,

```shell
$ jiratui issues update SCRUM-1 -p 1
```

This will allow you to set the priority of the work item with key `SCRUM-1` to High. See the
[metadata command](show-metadata) above for the context.

### Listing Comments

To list the comments of a work item use the `comments list` command and pass the (case-sensitive) key of the work
item whose comments you want to list.

```shell
$ jiratui comments list SCRUM-1

| ID | Issue Key | Author             | Created          | Updated          | Message      |
|----|-----------|--------------------|------------------|------------------|--------------|
| 1  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:09 | 2025-12-31 16:09 | Hello World! |
```

If you want to see the text of a specific comment use the `comments show` command and pass the (case-sensitive) key of
the work item followed by the ID of the comment.

```shell
$ jiratui comments show SCRUM-1 1

Hello World!
```

### Adding Comments

To add a comment to a work item use the `comments add` command and pass the (case-sensitive) key of the work
item and the comment string you want to add.

```shell
$ jiratui comments add SCRUM-1 'My new comment'

| ID | Issue Key | Author             | Created          | Updated          | Message        |
|----|-----------|--------------------|------------------|------------------|----------------|
| 1  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:09 | 2025-12-31 16:09 | Hello World!   |
| 2  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:29 | 2025-12-31 16:29 | My new comment |
```

### Deleting a Comment

```shell
$ jiratui comments delete SCRUM-1 2

Comment deleted successfully.

$ jiratui comments list SCRUM-1

| ID | Issue Key | Author             | Created          | Updated          | Message      |
|----|-----------|--------------------|------------------|------------------|--------------|
| 1  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:09 | 2025-12-31 16:09 | Hello World! |
```

### Search Users

You can search users with the command `users search` providing (part of) the name or email address of the
user. In the following example we are searching for any user whose name or email include the string `maggie`.

```shell
$ jiratui users search maggie

| Account ID | Active | Name           | Email Address      |
|------------|--------|----------------|--------------------|
| 1          | True   | maggie simpson | maggie@simpson.com |
```

### Searching User Groups

You can also search user groups. This is useful if you need to know the ID of a group. For example, if you need to set
up the value of the configuration option `jira_user_group_id`.

In order to list all the known user groups in your Jira instance you can use the command `users groups`. The command
accepts 2 optional arguments to paginate results: `--offset` and `--limit`.

```shell
$ jiratui users groups

| ID   | Name         | Total users in group? |
|------|--------------|-----------------------|
| 1    | admin users  | 2                     |
| 2    | developers   | 20                    |
```

You can also search groups by the (exact) name. For example,

```shell
$ jiratui users groups --group-names developers

| ID   | Name         | Total users in group? |
|------|--------------|-----------------------|
| 2    | developers   | 20                    |
```
