from jiratui.config import ApplicationConfiguration


def write_config(tmp_path, read_only: bool | None = None):
    lines = [
        'jira_api_username: user@example.test',
        'jira_api_token: token',
        'jira_api_base_url: https://example.atlassian.net',
    ]
    if read_only is not None:
        lines.append(f'read_only: {str(read_only).lower()}')
    config_file = tmp_path / 'config.yaml'
    config_file.write_text('\n'.join(lines))
    return config_file


def test_configuration_reads_read_only_from_yaml(tmp_path, monkeypatch):
    config_file = write_config(tmp_path, read_only=True)
    monkeypatch.setenv('JIRA_TUI_CONFIG_FILE', str(config_file))

    assert ApplicationConfiguration().read_only is True


def test_jira_tui_environment_variable_does_not_enable_read_only(tmp_path, monkeypatch):
    config_file = write_config(tmp_path)
    monkeypatch.setenv('JIRA_TUI_CONFIG_FILE', str(config_file))
    monkeypatch.setenv('JIRA_TUI_READ_ONLY', 'true')

    assert ApplicationConfiguration().read_only is False


def test_yaml_read_only_takes_priority_over_environment(tmp_path, monkeypatch):
    config_file = write_config(tmp_path, read_only=False)
    monkeypatch.setenv('JIRA_TUI_CONFIG_FILE', str(config_file))
    monkeypatch.setenv('JIRA_TUI_READ_ONLY', 'true')

    assert ApplicationConfiguration().read_only is False
