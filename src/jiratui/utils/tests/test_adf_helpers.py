from jiratui.utils.adf_helpers import (
    extract_mention_references,
    fix_adf_text_with_marks,
    format_mention_as_link,
    replace_media_with_text,
)


def test_extract_mention_references_single_mention():
    """Test extracting a single mention from ADF."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'mention',
                        'attrs': {
                            'id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                            'text': '@Placeholder User',
                        },
                    }
                ],
            }
        ],
    }

    result = extract_mention_references(adf)
    assert result == [
        {
            'account_id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'text': '@Placeholder User',
        }
    ]


def test_extract_mention_references_multiple_mentions():
    """Test extracting multiple mentions from ADF."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'mention',
                        'attrs': {
                            'id': '712020:abc',
                            'text': '@User One',
                        },
                    },
                    {'type': 'text', 'text': ' and '},
                    {
                        'type': 'mention',
                        'attrs': {
                            'id': '712020:def',
                            'text': '@User Two',
                        },
                    },
                ],
            }
        ],
    }

    result = extract_mention_references(adf)
    assert result == [
        {'account_id': '712020:abc', 'text': '@User One'},
        {'account_id': '712020:def', 'text': '@User Two'},
    ]


def test_extract_mention_references_no_mentions():
    """Test extracting from ADF with no mentions."""
    adf = {
        'type': 'doc',
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Just text'}]}],
    }

    result = extract_mention_references(adf)
    assert result == []


def test_extract_mention_references_nested_content():
    """Test extracting from nested ADF structures like list items."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'bulletList',
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {
                                        'type': 'mention',
                                        'attrs': {
                                            'id': '712020:nested',
                                            'text': '@Nested User',
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }

    result = extract_mention_references(adf)
    assert result == [{'account_id': '712020:nested', 'text': '@Nested User'}]


def test_extract_mention_references_missing_attrs():
    """Test extraction when mention node has malformed or missing attrs."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'mention',
                        'attrs': {},
                    }
                ],
            }
        ],
    }

    result = extract_mention_references(adf)
    assert result == []


def test_extract_mention_references_missing_account_id():
    """Test extraction when mention has text but no account_id."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'mention',
                        'attrs': {
                            'text': '@User Without ID',
                        },
                    }
                ],
            }
        ],
    }

    result = extract_mention_references(adf)
    assert result == []


def test_extract_mention_references_missing_text():
    """Test extraction when mention has account_id but no text."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'mention',
                        'attrs': {
                            'id': '712020:abc',
                        },
                    }
                ],
            }
        ],
    }

    result = extract_mention_references(adf)
    assert result == []


def test_extract_mention_references_multiple_in_different_contexts():
    """Test mentions in different contexts: paragraph, list, nested structures."""
    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'mention',
                        'attrs': {
                            'id': '712020:user1',
                            'text': '@User One',
                        },
                    }
                ],
            },
            {
                'type': 'bulletList',
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {
                                        'type': 'mention',
                                        'attrs': {
                                            'id': '712020:user2',
                                            'text': '@User Two',
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        ],
    }

    result = extract_mention_references(adf)
    assert len(result) == 2
    assert result[0] == {'account_id': '712020:user1', 'text': '@User One'}
    assert result[1] == {'account_id': '712020:user2', 'text': '@User Two'}


def test_format_mention_as_link_with_base_url():
    """Test formatting mention with base URL provided."""
    mention = {
        'account_id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        'text': '@Placeholder User',
    }
    base_url = 'https://example.atlassian.net'

    result = format_mention_as_link(mention, base_url)
    expected = '[@Placeholder User](https://example.atlassian.net/jira/people/xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)'
    assert result == expected


def test_format_mention_as_link_without_base_url():
    """Test formatting mention without base URL (fallback to plain text)."""
    mention = {
        'account_id': 'xxxxxx:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        'text': '@Placeholder User',
    }
    base_url = None

    result = format_mention_as_link(mention, base_url)
    assert result == '@Placeholder User'


def test_format_mention_as_link_empty_base_url():
    """Test formatting mention with empty string base URL."""
    mention = {
        'account_id': '712020:abc',
        'text': '@Test User',
    }
    base_url = ''

    result = format_mention_as_link(mention, base_url)
    assert result == '@Test User'


def test_format_mention_as_link_special_chars_in_account_id():
    """Test formatting with special characters in account ID."""
    mention = {
        'account_id': '712020:test-user_123.456',
        'text': '@Special User',
    }
    base_url = 'https://example.atlassian.net'

    result = format_mention_as_link(mention, base_url)
    expected = '[@Special User](https://example.atlassian.net/jira/people/712020:test-user_123.456)'
    assert result == expected


def test_fix_adf_text_with_marks():
    """Test fix_adf_text_with_marks strips trailing spaces from strong/em marked text.

    atlas_doc_parser outputs invalid markdown when text with marks has trailing spaces.
    Example: {text: "word ", marks: [{type: "strong"}]} → "**word **" (invalid)

    This function pre-processes ADF to strip trailing spaces from marked text nodes
    and inserts spacer text nodes for proper separation.
    """
    from atlas_doc_parser.api import parse_node

    adf = {
        'type': 'paragraph',
        'content': [
            {'type': 'text', 'text': 'Collaboration with ', 'marks': [{'type': 'strong'}]},
            {'type': 'mention', 'attrs': {'id': '123', 'text': '@Placeholder'}},
        ],
    }
    fixed = fix_adf_text_with_marks(adf)
    markdown = parse_node(fixed).to_markdown(ignore_error=True)
    assert '**Collaboration with** @Placeholder' in markdown

    adf = {
        'type': 'paragraph',
        'content': [
            {'type': 'text', 'text': 'This is '},
            {'type': 'text', 'text': 'important ', 'marks': [{'type': 'em'}]},
            {'type': 'text', 'text': 'text.'},
        ],
    }
    fixed = fix_adf_text_with_marks(adf)
    markdown = parse_node(fixed).to_markdown(ignore_error=True)
    assert '*important* text' in markdown

    adf = {
        'type': 'paragraph',
        'content': [
            {'type': 'text', 'text': 'Bold', 'marks': [{'type': 'strong'}]},
            {'type': 'text', 'text': ' text'},
        ],
    }
    fixed = fix_adf_text_with_marks(adf)
    markdown = parse_node(fixed).to_markdown(ignore_error=True)
    assert '**Bold** text' in markdown

    adf = {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Plain text '}]}
    fixed = fix_adf_text_with_marks(adf)
    assert fixed == adf  # Should return unchanged


def test_replace_media_with_text_single_attachment():
    """Test replacing a single mediaSingle node with inline text."""
    from atlas_doc_parser.api import parse_node

    adf = {
        'type': 'doc',
        'content': [
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'See image below:'}]},
            {
                'type': 'mediaSingle',
                'content': [{'type': 'media', 'attrs': {'alt': 'screenshot.png'}}],
            },
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'End of doc'}]},
        ],
    }

    result = replace_media_with_text(adf)
    markdown = parse_node(result).to_markdown(ignore_error=True)

    assert '*(See file "screenshot.png" in attachments tab)*' in markdown
    assert markdown.index('See image below') < markdown.index('*(See file')
    assert markdown.index('*(See file') < markdown.index('End of doc')


def test_replace_media_with_text_multiple_attachments():
    """Test replacing multiple mediaSingle nodes preserves order."""
    from atlas_doc_parser.api import parse_node

    adf = {
        'type': 'doc',
        'content': [
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'First:'}]},
            {
                'type': 'mediaSingle',
                'content': [{'type': 'media', 'attrs': {'alt': 'img1.png'}}],
            },
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Second:'}]},
            {
                'type': 'mediaSingle',
                'content': [{'type': 'media', 'attrs': {'alt': 'img2.jpg'}}],
            },
        ],
    }

    result = replace_media_with_text(adf)
    markdown = parse_node(result).to_markdown(ignore_error=True)

    assert '*(See file "img1.png" in attachments tab)*' in markdown
    assert '*(See file "img2.jpg" in attachments tab)*' in markdown
    assert markdown.index('img1.png') < markdown.index('img2.jpg')


def test_replace_media_with_text_no_attachments():
    """Test that ADF without mediaSingle nodes is unchanged."""

    adf = {
        'type': 'doc',
        'content': [
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Just text'}]},
        ],
    }

    result = replace_media_with_text(adf)
    assert result == adf


def test_replace_media_with_text_nested_in_list():
    """Test replacing mediaSingle nodes nested in list items."""
    from atlas_doc_parser.api import parse_node

    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'bulletList',
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Item 1'}]},
                            {
                                'type': 'mediaSingle',
                                'content': [{'type': 'media', 'attrs': {'alt': 'nested.png'}}],
                            },
                        ],
                    }
                ],
            }
        ],
    }

    result = replace_media_with_text(adf)
    markdown = parse_node(result).to_markdown(ignore_error=True)

    assert '*(See file "nested.png" in attachments tab)*' in markdown


def test_replace_media_with_text_missing_alt():
    """Test handling mediaSingle with missing alt attribute."""
    from atlas_doc_parser.api import parse_node

    adf = {
        'type': 'doc',
        'content': [
            {
                'type': 'mediaSingle',
                'content': [{'type': 'media', 'attrs': {'id': '123'}}],  # No alt
            }
        ],
    }

    result = replace_media_with_text(adf)
    markdown = parse_node(result).to_markdown(ignore_error=True)

    assert '*(See file "unknown" in attachments tab)*' in markdown
