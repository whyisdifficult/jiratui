# Configuration

Before using the application, you need to configure a few settings.

```{tip}
The application uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). This allows
you to define the configuration variables as ENV variables. To do that simply set the value of the config variable you
want to define in a ENV variable called `JIRA_TUI_*`; where `*` is the name of the config variable.

**Example**: to define the value of `jira_api_username` do this: `JIRA_TUI_JIRA_API_USERNAME=...`
```

## Setting Up the Jira's Instance API Credentials

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

You can pass the variable `JIRA_TUI_ENV_FILE` and point to the location of your env file.

### Use a Config File

You can also use a combination of a `.env` file and a config file. For example, keep the API username and token in the
`.env` file while placing the rest of the settings in a config file. The default config file expected by the application
is `jiratui.yaml`, but you can name your config file anything you like and specify it using the environment variable
`JIRA_TUI_CONFIG_FILE` when interacting with the CLI/app.

Example: Create a file called `my-jiratui-config.yaml` and add the following:

```yaml
jira_api_base_url: 'https://<your-jira-instance-hostname>.atlassian.net'
```

```{tip}
The application provides a sample config file called `jiratui.example.yaml` that you can use to define yours.
```

### Full Example

```shell
# ~/.env.jiratui
JIRA_TUI_JIRA_API_USERNAME=<your-jira-api-username>
JIRA_TUI_JIRA_API_TOKEN=<your-jira-api-token>
```

```shell
# ~/jiratui.yaml
jira_api_base_url: 'https://<your-jira-instance-hostname>.atlassian.net'
```

Now that you have the basic configuration you can [run the tool and its commands](/users/usage/index).
