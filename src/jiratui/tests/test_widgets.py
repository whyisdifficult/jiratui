from unittest.mock import MagicMock

import pytest

from jiratui.app import JiraApp
from jiratui.widgets.work_item_details.details import IssueSummaryField


@pytest.fixture()
def app(config_for_testing, jira_api_controller) -> JiraApp:
    app = JiraApp(config_for_testing)
    app.api = jira_api_controller
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
