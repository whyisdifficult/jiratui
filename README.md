# JiraTUI

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/whyisdifficult/jiratui/.github%2Fworkflows%2Ftest.yaml)
[![CodeQL](https://github.com/whyisdifficult/jiratui/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/whyisdifficult/jiratui/actions/workflows/github-code-scanning/codeql)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jiratui)
![GitHub Release](https://img.shields.io/github/v/release/whyisdifficult/jiratui)
[![PyPI version](https://badge.fury.io/py/jiratui.svg)](https://badge.fury.io/py/jiratui)
[![AUR package](https://repology.org/badge/version-for-repo/aur/jiratui.svg)](https://repology.org/project/jiratui/versions)
![Static Badge](https://img.shields.io/badge/OS-Linux%20MacOS%20Windows-orange)

A **Text User Interface (TUI)** for interacting with Atlassian Jira directly from your shell.

![The initial screen of JiraTUI](https://whyisdifficult.github.io/jiratui/assets/img/gallery/app-homepage.png "JiraTUI initial screen")

## Introduction

JiraTUI is built using the [Textual](https://textual.textualize.io/) and [Rich](https://rich.readthedocs.io/en/latest/)
frameworks.

It supports the [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/). Starting
with v1.1.0 JiraTUI supports [Jira REST API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/) as
well.

## Installation

The recommended way to install the application is via [uv](https://docs.astral.sh/uv/):

```shell
uv tool install jiratui
```

Alternatively, you can install it using `pip`:

```shell
pip install jiratui
```

or `pipx`:

```shell
pipx install jiratui
```

For Arch Linux (btw) the package is available in [AUR](https://aur.archlinux.org/packages/jiratui-git)

```shell
yay -S jiratui-git
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
  config    Shows the location of the configuration file.
  issues    Use it to search, update or delete work items.
  ui        Launches the Jira TUI application.
  users     Use it to search users and user groups.
  version   Shows the version of the tool.
  themes    List the available built-in themes.
```

You can check the installed version with

```shell
jiratui version
1.0.0
```

## Settings

Before using the application you need to provide the basic configuration. All the settings can be provided in a `yaml`
file.

The application uses the [XDG specification](https://specifications.freedesktop.org/basedir-spec/latest/) to locate
config (and log) files. The default name of the config file is `config.yaml`. You can override the location of the
config file via the env variable `JIRA_TUI_CONFIG_FILE`. The application will attempt to load the config
file in the following way:

1. If the variable `JIRA_TUI_CONFIG_FILE` is set it will use the file specified by it.
2. If not, if `XDG_CONFIG_HOME` is set then it will load the file `$XDG_CONFIG_HOME/jiratui/config.yaml`.
3. If not, it will attempt to load the file from `$HOME/.config/jiratui/config.yaml`.

**WARNING**: Starting with version `v1.0.0` the application no longer supports using the env variable
`JIRA_TUI_ENV_FILE` to define the `.env` file with configuration settings. Instead, all settings must be defined in the
config file as described below.

### Setting Up the Jira's Instance API

You must provide the following values to connect to your Jira instance API:

- `jira_api_username`: the username for connecting to your Jira API.
- `jira_api_token`: the token for connecting to your Jira API. This can be your Personal Access Token (PAT).
- `jira_api_base_url`: the base URL of your Jira instance API.

Example: Assuming that your config file is located at `$XDG_CONFIG_HOME/jiratui/config.yaml` you can add the following:

```yaml
jira_api_username: 'bart@simpson.com'
jira_api_token: '12345'
jira_api_base_url: 'https://<your-jira-instance-hostname>.atlassian.net'
```

**Tip**: The application provides a sample config file called `jiratui.example.yaml` that you can use to define yours.

### Choosing the API version

By default, JiraTUI uses the [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).
This is good when your Jira instance runs in the cloud. However, Jira also offers an on-premises installation mode and
in these cases the version of the API may not be v3 but v2 instead. To address this JiraTUI lets you choose which
version of the API you can use.

To set the version of the API update your config file to include:

```yaml
jira_api_version: 2
```

## Running the Application UI

Once you have provided the necessary settings, you can run the application's UI with the following command:

```shell
jiratui ui
```

If you are using a custom config file, run:

```shell
JIRA_TUI_CONFIG_FILE=/path/to/cutom-file/my-file.yaml jiratui ui
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

The full list of commands you can use with the CLI and additional settings is available at
[https://jiratui.readthedocs.io](https://jiratui.readthedocs.io/en/latest/index.html)

# Documentation

The full documentation is available at [https://jiratui.readthedocs.io](https://jiratui.readthedocs.io/en/latest/index.html)

# Contributing

If you would like to contribute to the project make sure you are familiar with the
[contribution guidelines](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

# Acknowledgements

This project was inspired by the work of [Textualize](https://www.textualize.io/) and their remarkable frameworks
[Textual](https://textual.textualize.io/) and [Rich](https://rich.readthedocs.io/en/latest/).

I also want to say thanks to the teams behind [Posting](https://posting.sh/),
[Lazygit](https://github.com/jesseduffield/lazygit) and [Harlequin](https://harlequin.sh/) for making these awesome
tools. These have become the must-have tools for my development workflow.

Last but not least to my colleagues [Tomasz](https://github.com/trojkat),
[Ilyes](https://github.com/ilyeshammadi) and [Giorgos](https://github.com/giorgosT) for their
support, encouragement and for reminding me how cool is to work from your terminal (something I have forgotten).
