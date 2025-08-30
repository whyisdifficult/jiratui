# JiraTUI

A **Text User Interface (TUI)** for interacting with Atlassian Jira directly from your shell.

![The initial screen of JiraTUI](https://whyisdifficult.github.io/jiratui/assets/img/gallery/app-homepage.png "JiraTUI initial screen")

## Installation

The recommended way to install the application is via [uv](https://docs.astral.sh/uv/):

```shell
uv add jiratui
```

Alternatively, you can install it using `pip`:

```shell
pip install jiratui
```

## Usage

After installing the package, you can run the CLI tool with the following command:

```shell
jiratui
```

This will show you the available commands for the CLI tool

```shell
Usage: jiratui [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  comments  Use it to add, list or delete comments associated to work items.
  issues    Use it to search, update or delete work items.
  ui        Launches the Jira TUI application.
  users     Use it to search users and user groups.
```

## Settings

Before using the application, you need to configure a few settings.

**Tip**: the application uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). This allows
you to define the configuration variables as ENV variables. To do that simply set the value of the config variable you
want to define in a ENV variable called `JIRA_TUI_*`; where `*` is the name of the config variable.

**Example**: to define the value of `jira_api_username` do this: `JIRA_TUI_JIRA_API_USERNAME=...`

## Setting Up the Jira's Instance API

You must provide the following values to connect to your Jira instance API:

- `jira_api_username`: the username for connecting to your Jira's API.
- `jira_api_token`: the token for connecting to your Jira's API.
- `jira_api_base_url`: the base URL of your Jira instance API.

You have a couple of options for setting these values.

### Use a `.env` File

Create a `.env` file named `.env.jiratui` and add the following content:

```yaml
JIRA_TUI_JIRA_API_USERNAME=<your-jira-api-username>
JIRA_TUI_JIRA_API_TOKEN=<your-jira-api-token>
JIRA_TUI_JIRA_API_BASE_URL=https://<your-jira-instance-hostname>.atlassian.net
```

### Use a Config File

You can also use a combination of a `.env` file and a config file. For example, keep the API username and token in the
`.env` file while placing the rest of the settings in a config file. The default config file expected by the application
is `jiratui.yaml`, but you can name your config file anything you like and specify it using the environment variable
`JIRA_TUI_CONFIG_FILE` when interacting with the CLI/app.

Example: Create a file called `my-jiratui-config.yaml` and add the following:

```yaml
jira_api_base_url: 'https://<your-jira-instance-hostname>.atlassian.net'
```

**Tip**: The application provides a sample config file called `jiratui.example.yaml` that you can use to define yours.

## Running the Application UI

Once you have provided the necessary settings, you can run the application's UI with the following command:

```shell
jiratui ui
```

If you are using a custom config file, run:

```shell
JIRA_TUI_CONFIG_FILE=my-file.yaml jiratui ui
```

## CLI Interface

In addition to the `ui` command, the CLI tool offers several commands to help you manage issues, comments, and users.

### Searching for Issues

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

To search for a specific work item, use the issues search command with the `--key` argument and the (case-sensitive)
issue key.

**Example**: searching for the issue with key `SCRUM-1`

```shell
$ jiratui issues search --key SCRUM-1

| Key     | Type | Created          | Status (ID)   | Reporter          | Assignee          | Summary                                    |
|---------|------|------------------|---------------|-------------------|-------------------|--------------------------------------------|
| SCRUM-1 | Bug  | 2025-07-31 15:55 | To Do (10000) | lisa@simpson.com  | bart@simpson.com  | Write 100 times "I will be a good student" |
```

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

# Documentation

The full documentation is available at [https://jiratui.readthedocs.io](https://jiratui.readthedocs.io/en/latest/index.html)

# Contributing

If you would like to contribute to the project make sure you are familiar with the
[contribution guidelines](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
