from unittest.mock import Mock

from click.testing import CliRunner

import jiratui.cli as cli_module
from jiratui.cli import cli


def test_ui_read_only_flag_enables_read_only_for_session(tmp_path, monkeypatch):
    config_file = tmp_path / 'config.yaml'
    config_file.write_text(
        '\n'.join(
            [
                'jira_api_username: user@example.test',
                'jira_api_token: token',
                'jira_api_base_url: https://example.atlassian.net',
                'read_only: false',
            ]
        )
    )
    monkeypatch.setenv('JIRA_TUI_CONFIG_FILE', str(config_file))
    app = Mock()
    monkeypatch.setattr(cli_module, 'JiraApp', app)

    result = CliRunner().invoke(cli, ['ui', '--read-only'])

    assert result.exit_code == 0, result.output
    assert app.call_args.args[0].read_only is True
    app.return_value.run.assert_called_once_with()
