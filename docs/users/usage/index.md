# Usage

## Launching the UI

Once you have provided the necessary settings, you can run the application's UI with the following command:

```shell
jtuicli ui
```

If you are using a custom config file, run:

```shell
JIRA_TUI_CONFIG_FILE=my-file.yaml jtuicli ui
```

## CLI Interface

In addition to the `ui` command, the CLI tool offers several commands to help you manage issues, comments, and users.

### Searching for Issues

To search for work items in the project `SCRUM`, use the issues search command and pass the `--project-key` argument
with the (case-sensitive) project key.

**Example**: searching for issues of the project `SCRUM`

```shell
$ jtuicli issues search --project-key SCRUM

| Key     | Type | Created          | Status (ID)   | Reporter          | Assignee          | Summary                                    |
|---------|------|------------------|---------------|-------------------|-------------------|--------------------------------------------|
| SCRUM-1 | Bug  | 2025-07-31 15:55 | To Do (10000) | lisa@simpson.com  | bart@simpson.com  | Write 100 times "I will be a good student" |
| SCRUM-2 | Task | 2025-06-30 15:56 | To Do (10000) | homer@simpson.com | homer@simpson.com | Eat donuts                                 |
```

To search for a specific work item, use the issues search command with the `--key` argument and the (case-sensitive)
issue key.

**Example**: searching for the issue with key `SCRUM-1`

```shell
$ jtuicli issues search --key SCRUM-1

| Key     | Type | Created          | Status (ID)   | Reporter          | Assignee          | Summary                                    |
|---------|------|------------------|---------------|-------------------|-------------------|--------------------------------------------|
| SCRUM-1 | Bug  | 2025-07-31 15:55 | To Do (10000) | lisa@simpson.com  | bart@simpson.com  | Write 100 times "I will be a good student" |
```

### Show Metadata

The tool also provides a command to show metadata associated to a work item. This is useful when you need to update a
work item; for example if you want to transition the state of the item and you need to know the ID of the state.

```shell
$ jtuicli issues metadata SCRUM-1

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

### Listing Comments

To list the comments of a work item use the `comments list` command and pass the (case-sensitive) key of the work
item whose comments you want to list.

```shell
$ jtuicli comments list SCRUM-1

| ID | Issue Key | Author             | Created          | Updated          | Message      |
|----|-----------|--------------------|------------------|------------------|--------------|
| 1  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:09 | 2025-12-31 16:09 | Hello World! |
```

If you want to see the text of a specific comment use the `comments show` command and pass the (case-sensitive) key of
the work item followed by the ID of the comment.

```shell
$ jtuicli comments show SCRUM-1 1

Hello World!
```

### Adding Comments

To add a comment to a work item use the `comments add` command and pass the (case-sensitive) key of the work
item and the comment string you want to add.

```shell
$ jtuicli comments add SCRUM-1 'My new comment'

| ID | Issue Key | Author             | Created          | Updated          | Message        |
|----|-----------|--------------------|------------------|------------------|----------------|
| 1  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:09 | 2025-12-31 16:09 | Hello World!   |
| 2  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:29 | 2025-12-31 16:29 | My new comment |
```

### Deleting a Comment

```shell
$ jtuicli comments delete SCRUM-1 2

Comment deleted successfully.

$ jtuicli comments list SCRUM-1

| ID | Issue Key | Author             | Created          | Updated          | Message      |
|----|-----------|--------------------|------------------|------------------|--------------|
| 1  | SCRUM-1   | maggie@simpson.com | 2025-12-31 16:09 | 2025-12-31 16:09 | Hello World! |
```

### Search Users

You can search users with the command `users search` providing (part of) the name or email address of the
user. In the following example we are searching for any user whose name or email include the string `maggie`.

```shell
$ jtuicli users search maggie

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
$ jtuicli users groups

| ID   | Name         | Total users in group? |
|------|--------------|-----------------------|
| 1    | admin users  | 2                     |
| 2    | developers   | 20                    |
```

You can also search groups by the (exact) name. For example,

```shell
$ jtuicli users groups --group-names developers

| ID   | Name         | Total users in group? |
|------|--------------|-----------------------|
| 2    | developers   | 20                    |
```
