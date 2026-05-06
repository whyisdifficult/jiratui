from marklas import to_adf, to_md


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
