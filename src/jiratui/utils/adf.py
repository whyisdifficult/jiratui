import re

from marklas import Transformer, parse_md, to_adf, to_md
from marklas.ast import Inline, LinkMark, Mark, Paragraph, Text


def convert_markdown_to_adf(content: str) -> dict:
    """Converts a Markdown string in CommonMark flavor to Atlassian's ADF.

    Args:
        content: the CommonMark Markdown string to convert to Atlassian's ADF.

    Returns:
        A dict representing the ADF element.
    """

    return to_adf(content)


def convert_adf_to_markdown(content: dict) -> str:
    """Converts Atlassian's ADF to a Markdown string in CommonMark flavor.

    Args:
        content: Atlassian's ADF dictionary.

    Returns:
        A CommonMark Markdown string.
    """

    return to_md(content)


# the links extracted from a Markdown content
links: list[dict] = []


def extract_web_links_from_markdown(content: str) -> list[dict]:
    """Extracts Web links from a Markdown string.

    Args:
        content: The Markdown string to extract Web Links from.

    Returns:
        A list of dictionaries with the links found in the text.

    Examples:
    links = extract_web_links_from_markdown('View link https://foo.bar and [this link](https://bar.foo)')
    links
    [
        {
            'title': 'https://foo.bar',
            'url': 'https://foo.bar',
        },
        {
            'title': 'this link',
            'url': 'https://bar.foo',
        }
    ]
    """

    link_parser_transformer = Transformer()

    @link_parser_transformer.register(Paragraph)
    def _process_paragraph(node: Paragraph) -> Paragraph | None:
        global links
        raw_urls_regex = re.compile(
            r'https?://[^\s\[\]()]+|ftp://[^\s\[\]()]+|(?:www\.)[^\s\[\]()]+|(?<![\(\[])(?<![a-zA-Z]\()(?:(?<!\()\b(?:[a-z]{2,}\.)+(com|org|net|edu|gov|io|co|uk)\b)',
            re.MULTILINE,
        )
        c: Inline
        m: Mark
        for c in node.content:
            if not isinstance(c, Text):
                continue
            link_text = c.text or ''
            for m in c.marks:
                if isinstance(m, LinkMark):
                    links.append({'url': m.href, 'title': m.title or link_text})
            # there may also be "raw" links in the text; i.e. w/o Markdown []() syntax. We need to extract these using a
            # regex
            if link_text:
                for link in raw_urls_regex.finditer(link_text):
                    if href := link.group():
                        links.append({'url': href, 'title': href})
        return node

    if not content:
        return []

    global links
    links = []
    ast_doc = parse_md(content)
    link_parser_transformer(ast_doc)
    return links[:] or []
