import re

from marklas import Transformer, parse_md, to_adf, to_md
from marklas.ast import LinkMark, Mark, Text


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


def extract_web_links_from_markdown(content: str) -> list[dict]:
    """Extracts Web links from a Markdown string.

    This function will return a list without duplicated urls. If a URL appears more than once in the document then the
    last occurrence is returned.

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

    @link_parser_transformer.register(Text)
    def _process_text(node: Text) -> Text | None:
        raw_urls_regex = re.compile(
            r'https?://[^\s\[\]()]+|ftp://[^\s\[\]()]+|(?:www\.)[^\s\[\]()]+|(?<![\(\[])(?<![a-zA-Z]\()(?:(?<!\()\b(?:[a-z]{2,}\.)+(com|org|net|edu|gov|io|co|uk)\b)',
            re.MULTILINE,
        )
        m: Mark
        link_text = node.text or ''
        for m in node.marks:
            if isinstance(m, LinkMark):
                links.append({'url': m.href, 'title': m.title or link_text})
        # there may also be "raw" links in the text; i.e. w/o Markdown []() syntax. We need to extract these using a
        # regex
        if link_text:
            for link in raw_urls_regex.finditer(link_text):
                if href := link.group():
                    links.append({'url': href, 'title': href})
        # return the unmodified node
        return node

    if not content:
        return []

    links: list[dict] = []
    ast_doc = parse_md(content)
    link_parser_transformer(ast_doc)
    # remove duplicated urls
    links_by_urls = {link.get('url'): link for link in links}
    return list(links_by_urls.values()) or []
