import pytest

from jiratui.models import IssueStatus, IssueType, JiraIssue, RelatedJiraIssue


def _jira_issue(summary: str) -> JiraIssue:
    return JiraIssue(
        id='1',
        key='TEST-1',
        summary=summary,
        status=IssueStatus(id='1', name='To Do'),
    )


def _related_jira_issue(summary: str) -> RelatedJiraIssue:
    return RelatedJiraIssue(
        id='1',
        key='TEST-1',
        summary=summary,
        status=IssueStatus(id='1', name='To Do'),
        issue_type=IssueType(id='1', name='Task'),
    )


@pytest.mark.parametrize('issue_factory', [_jira_issue, _related_jira_issue])
@pytest.mark.parametrize(
    'summary, max_length, expected',
    [
        ('  a summary  ', None, 'a summary'),  # strips whitespace, no truncation
        ('a summary', 0, 'a summary'),  # zero disables truncation
        ('a summary', -3, 'a summary'),  # negative values disable truncation
        ('short', 10, 'short'),  # shorter than the limit stays untouched
        ('exactlyten', 10, 'exactlyten'),  # exactly the limit stays untouched
        ('a summary that is quite long', 20, 'a summary that is...'),  # truncated to max_length
        ('long summary here', 4, 'l...'),  # suffix fits within max_length
        ('long summary here', 3, 'lon'),  # max_length <= len('...') cuts without suffix
        ('long summary here', 2, 'lo'),
        ('   ', None, ''),
    ],
)
def test_cleaned_summary(issue_factory, summary, max_length, expected):
    assert issue_factory(summary).cleaned_summary(max_length) == expected
