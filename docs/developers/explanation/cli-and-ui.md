# JiraTUI Applications

JiraTUI provides 2 applications to users.

- **UI Application**: this is the main application of the tool. It provides a UI to interact with your organization's Jira
instance directly from the terminal. The application is built using [Textual](https://textual.textualize.io/) and
[Rich](https://rich.readthedocs.io/en/latest/introduction.html).

To run the UI in development mode using Textual you can execute the following:

```shell
JIRA_TUI_CONFIG_FILE=path/to/config.yaml textual run --dev src/jiratui/cli.py ui
```

- **CLI**: this is rather simple application that provides a small number of commands to carry out some basic tasks. The
application is built using [Click](https://click.palletsprojects.com/en/stable/) and
[Rich](https://rich.readthedocs.io/en/latest/introduction.html).

To run the UI in development mode using Textual you can execute the following:

```shell
JIRA_TUI_CONFIG_FILE=path/to/config.yaml textual run --dev src/jiratui/cli.py
```
