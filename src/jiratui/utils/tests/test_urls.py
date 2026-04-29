from unittest.mock import MagicMock, patch

import pytest

from jiratui.utils.urls import (
    build_external_url_for_attachment,
    build_external_url_for_comment,
    build_external_url_for_issue,
    build_external_url_for_work_log,
)


@pytest.fixture()
def mock_configuration():
    with patch('jiratui.utils.urls.CONFIGURATION') as mock_config_var:
        mock_config = MagicMock()
        mock_config_var.get.return_value = mock_config
        yield mock_config


def test_build_external_url_for_issue(mock_configuration):
    mock_configuration.jira_base_url = 'http://foo.bar'
    result = build_external_url_for_issue('WI-1')
    assert result == 'http://foo.bar/browse/WI-1'


def test_build_external_url_for_issue_with_api_base_url(mock_configuration):
    mock_configuration.jira_base_url = ''
    mock_configuration.jira_api_base_url = 'http://bar.foo'
    result = build_external_url_for_issue('WI-1')
    assert result == 'http://bar.foo/browse/WI-1'


def test_build_external_url_for_comment(mock_configuration):
    mock_configuration.jira_base_url = 'http://foo.bar'
    result = build_external_url_for_comment('WI-1', '1')
    assert result == 'http://foo.bar/browse/WI-1?focusedCommentId=1'


def test_build_external_url_for_comment_with_api_base_url(mock_configuration):
    mock_configuration.jira_base_url = ''
    mock_configuration.jira_api_base_url = 'http://bar.foo'
    result = build_external_url_for_comment('WI-1', '1')
    assert result == 'http://bar.foo/browse/WI-1?focusedCommentId=1'


def test_build_external_url_for_work_log(mock_configuration):
    mock_configuration.jira_base_url = 'http://foo.bar'
    result = build_external_url_for_work_log('WI-1', '1')
    assert result == 'http://foo.bar/browse/WI-1?focusedWorklogId=1'


def test_build_external_url_for_work_log_with_api_base_url(mock_configuration):
    mock_configuration.jira_base_url = ''
    mock_configuration.jira_api_base_url = 'http://bar.foo'
    result = build_external_url_for_work_log('WI-1', '1')
    assert result == 'http://bar.foo/browse/WI-1?focusedWorklogId=1'


def test_build_external_url_for_attachment_without_attachment_id(mock_configuration):
    mock_configuration.jira_base_url = 'http://foo.bar'
    result = build_external_url_for_attachment('', 'file.txt')
    assert result is None


def test_build_external_url_for_attachment_without_filename(mock_configuration):
    mock_configuration.jira_base_url = 'http://foo.bar'
    result = build_external_url_for_attachment('1', '')
    assert result is None


def test_build_external_url_for_attachment(mock_configuration):
    mock_configuration.jira_base_url = 'http://foo.bar'
    result = build_external_url_for_attachment('attachment-1', 'file.txt')
    assert result == 'http://foo.bar/secure/attachment/attachment-1/file.txt'


def test_build_external_url_for_attachment_with_api_base_url(mock_configuration):
    mock_configuration.jira_base_url = ''
    mock_configuration.jira_api_base_url = 'http://bar.foo'
    result = build_external_url_for_attachment('attachment-1', 'file.txt')
    assert result == 'http://bar.foo/secure/attachment/attachment-1/file.txt'
