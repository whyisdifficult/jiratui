import pytest

from jiratui.utils.html import html_to_text_if_needed


@pytest.mark.parametrize(
    ('content', 'expected'),
    [
        ('Plain Jira text', 'Plain Jira text'),
        ('2 < 3 and 5 > 4', '2 < 3 and 5 > 4'),
        ('Use List<T> for this value', 'Use List<T> for this value'),
        ('<p>Hello <strong>world</strong></p>', 'Hello world'),
        ('<p>First<br>second</p><p>Third</p>', 'First\nsecond\nThird'),
        ('<ul><li>One</li><li>Two &amp; three</li></ul>', '- One\n- Two & three'),
        ('<p>Visible</p><script>alert(1)</script><style>.x { color: red; }</style>', 'Visible'),
    ],
)
def test_html_to_text_if_needed(content: str, expected: str):
    assert html_to_text_if_needed(content) == expected
