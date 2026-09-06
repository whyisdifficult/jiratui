"""Utilities for presenting HTML returned by Jira Data Center as readable text."""

from html.parser import HTMLParser
import re

_HTML_TAG_RE = re.compile(
    r'</?(?:a|address|article|aside|b|blockquote|br|code|div|em|footer|h[1-6]|header|i|li|ol|p|pre|'
    r'script|section|span|strong|style|table|tbody|td|th|thead|tr|ul)\b[^>]*>',
    re.IGNORECASE,
)


class _HTMLToTextParser(HTMLParser):
    """Convert common Jira-rendered HTML into terminal-friendly plain text."""

    _BLOCK_TAGS = {
        'address',
        'article',
        'aside',
        'blockquote',
        'div',
        'footer',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'header',
        'p',
        'pre',
        'section',
        'table',
        'tr',
        'ul',
        'ol',
    }
    _IGNORED_TAGS = {'script', 'style'}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._IGNORED_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == 'br':
            self._parts.append('\n')
        elif tag == 'li':
            self._ensure_newline()
            self._parts.append('- ')
        elif tag == 'td' or tag == 'th':
            if self._parts and not self._parts[-1].endswith(('\n', '\t')):
                self._parts.append('\t')
        elif tag in self._BLOCK_TAGS:
            self._ensure_newline()

    def handle_endtag(self, tag: str) -> None:
        if tag in self._IGNORED_TAGS:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return
        if self._ignored_depth:
            return
        if tag in self._BLOCK_TAGS or tag == 'li':
            self._ensure_newline()

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self._parts.append(data)

    def _ensure_newline(self) -> None:
        if self._parts and not self._parts[-1].endswith('\n'):
            self._parts.append('\n')

    def text(self) -> str:
        text = ''.join(self._parts)
        text = re.sub(r'[ \t]+\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


def html_to_text_if_needed(content: str) -> str:
    """Return readable text for HTML strings while leaving ordinary text unchanged."""

    if not _HTML_TAG_RE.search(content):
        return content

    parser = _HTMLToTextParser()
    parser.feed(content)
    parser.close()
    return parser.text()
