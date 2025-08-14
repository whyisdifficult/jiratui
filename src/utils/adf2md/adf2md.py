from src.utils.adf2md import markdown, nodes
from src.utils.adf2md.nodes import Node


def adf2md(json_data: dict | list[dict]) -> str:
    root_nodes: list[Node] = []

    if isinstance(json_data, list):
        root_nodes = nodes.create_nodes_from_list(json_data)
    elif isinstance(json_data, dict):
        if root_node := nodes.create_node_from_dict(json_data):
            root_nodes.append(root_node)

    md_text_list: list[str] = [markdown.gen_md_from_root_node(node) for node in root_nodes]

    if len(md_text_list) == 0:
        return ''

    return '\n\n'.join(md_text_list)
