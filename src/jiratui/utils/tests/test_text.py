import pytest
from textual.widgets import TextArea

from jiratui.utils.text import char_at_location_matches


@pytest.mark.parametrize(
    'text_content, result',
    [
        ('Hello world\nbart@simpson', True),
        ('', False),
    ],
)
def test_char_at_location_matches(text_content, result):
    # GIVEN
    widget = TextArea(text_content)
    # WHEN/THEN
    assert char_at_location_matches(widget, 1, 4, '@') is result
