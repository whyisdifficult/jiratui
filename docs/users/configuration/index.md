# Basic Configuration

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

For a full list of all the configuration options available and how to use them please refer to
[the settings reference guide](/users/configuration/reference.md).

## Jira API Credentials

You must provide the following values to connect to your Jira instance API:

- `jira_api_username`: the username for connecting to your Jira API.
- `jira_api_token`: the token for connecting to your Jira API. This can be your Personal Access Token (PAT).
- `jira_api_base_url`: the base URL of your Jira API.

Example: Assuming that your config file is located at `$XDG_CONFIG_HOME/jiratui/config.yaml` you can add the following:

```yaml
jira_api_username: 'bart@simpson.com'
jira_api_token: '12345'
jira_api_base_url: 'https://<your-jira-instance-hostname>.atlassian.net'
```

**Tip**: The application provides a sample config file called `jiratui.example.yaml` that you can use to define yours.

```{tip}
The application provides a sample config file called `jiratui.example.yaml` that you can use to define yours.
```

## Choosing the API version

JiraTUI supports the [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/). However,
starting with v1.1.0 JiraTUI supports [Jira REST API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/) as
well.

By default, JiraTUI uses the [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).
This is good when your Jira instance runs in the cloud. However, Jira also offers an on-premises installation mode and
in these cases the version of the API may not be v3 but v2 instead. To address this JiraTUI lets you choose which
version of the API you can use.

To set the version of the API update your config file to include:

```yaml
jira_api_version: 2
```

Now that you have the basic configuration you can [run the tool and its commands](/users/usage/index).
