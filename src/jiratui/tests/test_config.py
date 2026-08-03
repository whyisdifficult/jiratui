from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

import pytest
import yaml

from jiratui.config import ApplicationConfiguration, SSLConfiguration


@pytest.fixture
def yaml_config_file():
    """Fixture that creates a temporary YAML file"""

    def _create_yaml(content: str) -> dict:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            f.flush()

            with open(f.name) as config_file:
                config_dict = yaml.safe_load(config_file)

            Path(f.name).unlink()
            return config_dict

    return _create_yaml


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


@patch.object(ApplicationConfiguration, '_get_config_file')
def test_valid_config_when_ssl_is_missing(get_config_file_mock: Mock, yaml_config_file):
    # GIVEN
    get_config_file_mock.return_value = ''
    config_dict = yaml_config_file(
        """
        jira_api_username: 'bart'
        jira_api_token: '12345'
        jira_api_base_url: 'foo.bar'
        """
    )
    # WHEN
    config = ApplicationConfiguration(**config_dict)
    # THEN
    assert config.ssl is None


@patch.object(ApplicationConfiguration, '_get_config_file')
def test_valid_config_when_ssl_is_partially_configured(
    get_config_file_mock: Mock, yaml_config_file
):
    # GIVEN
    get_config_file_mock.return_value = ''
    config_dict = yaml_config_file(
        """
        jira_api_username: 'bart'
        jira_api_token: '12345'
        jira_api_base_url: 'foo.bar'
        ssl:
            verify_ssl: true
        """
    )
    # WHEN
    config = ApplicationConfiguration(**config_dict)
    # THEN
    assert config.ssl is not None
    assert isinstance(config.ssl, SSLConfiguration)
    assert config.ssl.verify_ssl is True


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
