from jiratui.utils.adf2md import markdown
from jiratui.utils.adf2md.nodes import Node, create_node_from_dict, create_nodes_from_list


def adf2md(json_data: dict | list[dict]) -> str:
    """Converts Atlassian's JIRA's ADF json-encoded string (Atlassian Document Format) to a Markdown string.

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/

    Args:
        json_data: the dictionary or list of dictionaries that should be converted to Markdown.

    Returns:
        A string with Markdown content.
    """
    root_nodes: list[Node] = []

    if isinstance(json_data, list):
        root_nodes = create_nodes_from_list(json_data)
    elif isinstance(json_data, dict):
        if root_node := create_node_from_dict(json_data):
            root_nodes.append(root_node)

    md_text_list: list[str] = [markdown.gen_md_from_root_node(node) for node in root_nodes]

    if len(md_text_list) == 0:
        return ''

    return '\n\n'.join(md_text_list)
