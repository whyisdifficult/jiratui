from jiratui.models import IssueComment, IssueStatus, JiraIssue, JiraUser, JiraWorklog


class TestAtlasDocParserIntegration:
    """Test that models correctly use atlas_doc_parser for ADF to Markdown conversion"""

    def test_issue_comment_get_body_with_adf(self):
        """Test IssueComment.get_body() converts ADF to markdown"""
        adf_body = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'This is a '},
                        {'type': 'text', 'text': 'test', 'marks': [{'type': 'strong'}]},
                        {'type': 'text', 'text': ' comment'},
                    ],
                }
            ],
        }

        comment = IssueComment(
            id='123',
            author=JiraUser(account_id='user1', active=True, display_name='Test User'),
            body=adf_body,
        )

        result = comment.get_body()
        assert 'test' in result
        assert result.strip() != ''

    def test_issue_comment_get_body_with_string(self):
        """Test IssueComment.get_body() handles plain string body"""
        comment = IssueComment(
            id='123',
            author=JiraUser(account_id='user1', active=True, display_name='Test User'),
            body='Plain text body',
        )

        result = comment.get_body()
        assert result == 'Plain text body'

    def test_issue_comment_get_body_with_none(self):
        """Test IssueComment.get_body() handles None body"""
        comment = IssueComment(
            id='123',
            author=JiraUser(account_id='user1', active=True, display_name='Test User'),
            body=None,
        )

        result = comment.get_body()
        assert result == ''

    def test_jira_issue_get_description_with_adf(self):
        """Test JiraIssue.get_description() converts ADF to markdown"""
        adf_description = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'heading',
                    'attrs': {'level': 1},
                    'content': [{'type': 'text', 'text': 'Description'}],
                },
                {
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': 'Issue description here'}],
                },
            ],
        }

        issue = JiraIssue(
            id='1',
            key='TEST-1',
            summary='Test issue',
            status=IssueStatus(id='1', name='Open'),
            description=adf_description,
        )

        result = issue.get_description()
        assert 'Description' in result
        assert 'Issue description here' in result

    def test_jira_issue_get_description_with_string(self):
        """Test JiraIssue.get_description() handles plain string description"""
        issue = JiraIssue(
            id='1',
            key='TEST-1',
            summary='Test issue',
            status=IssueStatus(id='1', name='Open'),
            description='Plain text description',
        )

        result = issue.get_description()
        assert result == 'Plain text description'

    def test_jira_issue_get_description_with_none(self):
        """Test JiraIssue.get_description() handles None description"""
        issue = JiraIssue(
            id='1',
            key='TEST-1',
            summary='Test issue',
            status=IssueStatus(id='1', name='Open'),
            description=None,
        )

        result = issue.get_description()
        assert result == ''

    def test_jira_worklog_get_comment_with_adf(self):
        """Test JiraWorklog.get_comment() converts ADF to markdown"""
        adf_comment = {
            'type': 'doc',
            'version': 1,
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Worklog comment'}]}
            ],
        }

        worklog = JiraWorklog(id='1', issue_id='TEST-1', comment=adf_comment)

        result = worklog.get_comment()
        assert 'Worklog comment' in result

    def test_jira_worklog_get_comment_with_string(self):
        """Test JiraWorklog.get_comment() handles plain string comment (Jira DC)"""
        worklog = JiraWorklog(id='1', issue_id='TEST-1', comment='Plain text comment')

        result = worklog.get_comment()
        assert result == 'Plain text comment'

    def test_jira_worklog_get_comment_with_none(self):
        """Test JiraWorklog.get_comment() handles None comment"""
        worklog = JiraWorklog(id='1', issue_id='TEST-1', comment=None)

        result = worklog.get_comment()
        assert result == ''


class TestMentionIntegration:
    """Test mention parsing integration in models"""

    def test_issue_comment_get_body_with_mentions_and_base_url(self):
        """Test IssueComment.get_body() formats mentions as links when base_url provided"""
        adf_body = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'Hey '},
                        {
                            'type': 'mention',
                            'attrs': {
                                'id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                                'text': '@Placeholder User',
                            },
                        },
                        {'type': 'text', 'text': ' can you review?'},
                    ],
                }
            ],
        }

        comment = IssueComment(
            id='123',
            author=JiraUser(account_id='user1', active=True, display_name='Test User'),
            body=adf_body,
        )

        result = comment.get_body(base_url='https://example.atlassian.net')
        assert '[@Placeholder User]' in result
        assert (
            'https://example.atlassian.net/jira/people/xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
            in result
        )

    def test_jira_issue_get_description_with_mentions_and_base_url(self):
        """Test JiraIssue.get_description() formats mentions as links when base_url provided"""
        adf_description = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'Assigned to '},
                        {
                            'type': 'mention',
                            'attrs': {
                                'id': '712020:xyz',
                                'text': '@Developer',
                            },
                        },
                    ],
                }
            ],
        }

        issue = JiraIssue(
            id='1',
            key='TEST-1',
            summary='Test issue',
            status=IssueStatus(id='1', name='Open'),
            description=adf_description,
        )

        result = issue.get_description(base_url='https://example.atlassian.net')
        assert '[@Developer]' in result
        assert 'https://example.atlassian.net/jira/people/712020:xyz' in result

    def test_jira_worklog_get_comment_with_mentions_and_base_url(self):
        """Test JiraWorklog.get_comment() formats mentions as links when base_url provided"""
        adf_comment = {
            'type': 'doc',
            'version': 1,
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'Discussed with '},
                        {
                            'type': 'mention',
                            'attrs': {
                                'id': '712020:manager',
                                'text': '@Manager',
                            },
                        },
                    ],
                }
            ],
        }

        worklog = JiraWorklog(id='1', issue_id='TEST-1', comment=adf_comment)

        result = worklog.get_comment(base_url='https://example.atlassian.net')
        assert '[@Manager]' in result
        assert 'https://example.atlassian.net/jira/people/712020:manager' in result


class TestMediaSingleNodeHandling:
    """Test mediaSingle node (attachments) handling in models."""

    def test_issue_description_with_mediasingle_attachment(self):
        """Test that descriptions with mediaSingle attachments render text content."""
        adf_with_attachment = {
            'version': 1,
            'type': 'doc',
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'Can not work with Womba. Need a new token.'}
                    ],
                },
                {
                    'type': 'mediaSingle',  # Unsupported node type
                    'attrs': {'layout': 'center'},
                    'content': [
                        {
                            'type': 'media',
                            'attrs': {
                                'id': '1722f971-f315-4d4b-8203-e794b2096561',
                                'type': 'file',
                                'collection': '',
                                'alt': 'Screenshot.png',
                            },
                        }
                    ],
                },
            ],
        }

        issue = JiraIssue(
            id='123',
            key='TEST-1',
            description=adf_with_attachment,
            summary='Test issue',
            status=IssueStatus(id='1', name='Open'),
        )

        description = issue.get_description()
        assert 'Can not work with Womba' in description
        assert 'Need a new token' in description
        assert description.strip() != ''

    def test_comment_with_mediasingle_attachment(self):
        """Test that comments with mediaSingle attachments render text content."""
        adf_with_attachment = {
            'version': 1,
            'type': 'doc',
            'content': [
                {
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': 'See attached screenshot'}],
                },
                {
                    'type': 'mediaSingle',
                    'attrs': {'layout': 'center'},
                    'content': [
                        {
                            'type': 'media',
                            'attrs': {'id': 'abc123', 'type': 'file', 'alt': 'image.png'},
                        }
                    ],
                },
            ],
        }

        comment = IssueComment(
            id='1',
            author=JiraUser(account_id='user1', active=True, display_name='Test User'),
            body=adf_with_attachment,
        )

        body = comment.get_body()
        assert 'See attached screenshot' in body
        assert body.strip() != ''

    def test_worklog_with_mediasingle_attachment(self):
        """Test that worklogs with mediaSingle attachments render text content."""
        adf_with_attachment = {
            'version': 1,
            'type': 'doc',
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Worked on bug fix'}]},
                {
                    'type': 'mediaSingle',
                    'attrs': {'layout': 'center'},
                    'content': [{'type': 'media', 'attrs': {'id': 'xyz', 'type': 'file'}}],
                },
            ],
        }

        worklog = JiraWorklog(id='1', issue_id='TEST-1', comment=adf_with_attachment)

        comment_text = worklog.get_comment()
        assert 'Worked on bug fix' in comment_text
        assert comment_text.strip() != ''

    def test_media_reference_text_in_description(self):
        """Test that media references show '(See file ... in attachments tab)' text."""
        adf_with_attachment = {
            'version': 1,
            'type': 'doc',
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Main text'}]},
                {
                    'type': 'mediaSingle',
                    'attrs': {'layout': 'center'},
                    'content': [
                        {
                            'type': 'media',
                            'attrs': {'id': '123', 'type': 'file', 'alt': 'MyScreenshot.png'},
                        }
                    ],
                },
            ],
        }

        issue = JiraIssue(
            id='1',
            key='TEST-1',
            description=adf_with_attachment,
            summary='Test',
            status=IssueStatus(id='1', name='Open'),
        )

        description = issue.get_description()

        assert 'Main text' in description

        assert '*(See file' in description
        assert 'MyScreenshot.png' in description
        assert 'attachments tab)*' in description

    def test_multiple_media_references(self):
        """Test that multiple attachments show multiple reference lines."""
        adf_with_two_attachments = {
            'version': 1,
            'type': 'doc',
            'content': [
                {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Text'}]},
                {
                    'type': 'mediaSingle',
                    'attrs': {'layout': 'center'},
                    'content': [
                        {'type': 'media', 'attrs': {'alt': 'first.png', 'type': 'file', 'id': '1'}}
                    ],
                },
                {
                    'type': 'mediaSingle',
                    'attrs': {'layout': 'center'},
                    'content': [
                        {'type': 'media', 'attrs': {'alt': 'second.jpg', 'type': 'file', 'id': '2'}}
                    ],
                },
            ],
        }

        issue = JiraIssue(
            id='1',
            key='TEST-1',
            description=adf_with_two_attachments,
            summary='Test',
            status=IssueStatus(id='1', name='Open'),
        )

        description = issue.get_description()

        assert 'first.png' in description
        assert 'second.jpg' in description
        assert description.count('See file') == 2
