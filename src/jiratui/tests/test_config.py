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
