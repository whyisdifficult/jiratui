# Installation

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

After installing the package, you can run the CLI tool with the following command:

```shell
jiratui --help
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

Before you can launch the UI or use the CLI's commands you need to configure a few things. Head over to the
[configuration section](/users//configuration/index) to see how to do that.
