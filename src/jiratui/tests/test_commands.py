import io
from unittest.mock import Mock

import pytest
from rich.console import Console

from jiratui.commands.render import JiraIssueSearchRenderer
from jiratui.config import CONFIGURATION, ApplicationConfiguration
from jiratui.models import IssueStatus, IssueType, JiraIssue, JiraIssueSearchResponse


@pytest.fixture()
def configuration():
    config_mock = Mock(spec=ApplicationConfiguration)
    token = CONFIGURATION.set(config_mock)
    yield config_mock
    CONFIGURATION.reset(token)


def _rendered_search_results(console_file: io.StringIO, summary: str) -> str:
    issue = JiraIssue(
        id='1',
        key='TEST-1',
        summary=summary,
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='1', name='Task'),
    )
    console = Console(file=console_file, width=250)
    JiraIssueSearchRenderer().render(console, JiraIssueSearchResponse(issues=[issue]))
    return console_file.getvalue()


def test_search_renderer_truncates_summary_using_cli_config(configuration):
    configuration.configure_mock(cli_search_results_truncate_work_item_summary=10)
    output = _rendered_search_results(io.StringIO(), 'a much longer summary')
    assert 'a much ...' in output
    assert 'longer' not in output


@pytest.mark.parametrize(
    'config_value',
    (0, None),
    ids=('zero', 'None'),
)
def test_search_renderer_does_not_truncate_summary_when_cli_config_is_unset(
    configuration, config_value
):
    configuration.configure_mock(cli_search_results_truncate_work_item_summary=config_value)
    output = _rendered_search_results(io.StringIO(), 'the full summary is shown')
    assert 'the full summary is shown' in output
