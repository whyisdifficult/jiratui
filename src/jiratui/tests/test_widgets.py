from unittest.mock import MagicMock, Mock

import pytest

from jiratui.api_controller.controller import APIController
from jiratui.app import JiraApp
from jiratui.config import ApplicationConfiguration
from jiratui.widgets.work_item_details.details import IssueSummaryField


@pytest.fixture()
def app() -> JiraApp:
    config_mock = Mock(spec=ApplicationConfiguration)
    config_mock.configure_mock(
        jira_api_base_url='foo.bar',
        jira_api_username='foo',
        jira_api_token='bar',
        jira_api_version=3,
        ignore_users_without_email=True,
        default_project_key_or_id=None,
        jira_account_id=None,
        jira_user_group_id='qwerty',
        tui_title=None,
        tui_title_include_jira_server_title=False,
        on_start_up_only_fetch_projects=False,
        log_file='',
        log_level='ERROR',
        theme=None,
    )
    app = JiraApp(config_mock)
    app.api = APIController(config_mock)
    app._setup_logging = MagicMock()  # type:ignore[method-assign]
    return app


@pytest.mark.parametrize('widget_value, expected_value', [('a summary ', 'a summary'), ('', '')])
@pytest.mark.asyncio
async def test_issue_summary_field(widget_value, expected_value, app):
    async with app.run_test():
        widget = IssueSummaryField()
        widget.value = widget_value
        result = widget.validated_summary
        assert result == expected_value
