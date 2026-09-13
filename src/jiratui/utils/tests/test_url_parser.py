from jiratui.utils.adf import extract_web_links_from_markdown

markdown = """# Sample Markdown with Different URL Formats

## URLs in Paragraphs

This is a paragraph with a **markdown-style link** to [DuckDuckGo's search engine](https://www.duckduckgo.com). You can
also include raw URLs directly in text, like https://www.example.com or www.github.com, and they'll typically be
recognized as links by markdown processors.

Another paragraph might reference a URL in different contexts: Visit https://www.wikipedia.org for general knowledge,
or check out [this helpful guide](https://www.w3schools.com/html/) if you're learning web development.

## URLs in Bullet Lists

Here are some useful resources organized as bullet points:

- [Python Official Documentation](https://www.python.org/doc/?query=1&answer=42#section-a) - Learn Python programming
- https://www.stackoverflow.com - Get answers to coding questions
- Visit www.udemy.com for online courses
- [MDN Web Docs](https://developer.mozilla.org) - Comprehensive web technology reference
- Raw URL example: https://www.medium.com

## URLs in Numbered Lists

Follow these steps to get started:

1. Go to [GitHub](https://www.github.com) and create an account
2. Clone a repository from https://github.com/some-project
3. Read the documentation at www.docs.example.com
4. Follow the [installation guide](https://www.example.com/install)
5. Visit https://www.npmjs.com to find packages

## Mixed Formats in a Table

| Resource | Link | Type |
|----------|------|------|
| Search Engine | [DuckDuckGo](https://www.duckduckgo.com) | Markdown link |
| Video Platform | https://www.youtube.com | Raw URL |
| Learning | www.codecademy.com | www. format |
| Community | [Stack Overflow](https://www.stackoverflow.com) | Markdown link |

## Additional Examples

You can also use **reference-style links** like this: Check out [this resource][1] for more information.

[1]: https://www.example.com/resource

Or simply drop URLs inline without any formatting at all: https://www.rust-lang.org or www.golang.org
"""


def test_extract_web_links_from_markdown():
    # WHEN
    result = extract_web_links_from_markdown(markdown)
    # THEN
    assert result == [
        {
            'url': 'https://www.duckduckgo.com',
            'title': 'DuckDuckGo',
        },
        {
            'url': 'https://www.example.com',
            'title': 'https://www.example.com',
        },
        {
            'url': 'www.github.com,',
            'title': 'www.github.com,',
        },
        {
            'url': 'https://www.wikipedia.org',
            'title': 'https://www.wikipedia.org',
        },
        {
            'url': 'https://www.w3schools.com/html/',
            'title': 'this helpful guide',
        },
        {
            'url': 'https://www.python.org/doc/?query=1&answer=42#section-a',
            'title': 'Python Official Documentation',
        },
        {
            'url': 'https://www.stackoverflow.com',
            'title': 'Stack Overflow',
        },
        {
            'url': 'www.udemy.com',
            'title': 'www.udemy.com',
        },
        {
            'url': 'https://developer.mozilla.org',
            'title': 'MDN Web Docs',
        },
        {
            'url': 'https://www.medium.com',
            'title': 'https://www.medium.com',
        },
        {
            'url': 'https://www.github.com',
            'title': 'GitHub',
        },
        {
            'url': 'https://github.com/some-project',
            'title': 'https://github.com/some-project',
        },
        {
            'url': 'www.docs.example.com',
            'title': 'www.docs.example.com',
        },
        {'url': 'https://www.example.com/install', 'title': 'installation guide'},
        {
            'url': 'https://www.npmjs.com',
            'title': 'https://www.npmjs.com',
        },
        {
            'url': 'https://www.youtube.com',
            'title': 'https://www.youtube.com',
        },
        {
            'url': 'www.codecademy.com',
            'title': 'www.codecademy.com',
        },
        {
            'url': 'https://www.example.com/resource',
            'title': 'this resource',
        },
        {
            'url': 'https://www.rust-lang.org',
            'title': 'https://www.rust-lang.org',
        },
        {
            'url': 'www.golang.org',
            'title': 'www.golang.org',
        },
    ]
