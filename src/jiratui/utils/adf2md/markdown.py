from typing import Optional

from jiratui.utils.adf2md.nodes import Node, NodeType


def gen_md_from_root_node(root_node: Node) -> str:
    try:
        root_node_presenter = create_node_presenter_from_node(root_node, True, False)
    except Exception:
        return ''
    return str(root_node_presenter)


class NodePresenter(object):
    _node: Node
    _child_presenters: list

    def __init__(self, node: Node):
        self._node = node
        self._child_presenters = []

        idx = 0
        cur_node_type = None
        for child in self._node.child_nodes:
            child_presenter = create_node_presenter_from_node(
                child, idx == 0, cur_node_type == NodeType.HARD_BREAK, self._node
            )
            if not child_presenter:
                # print(f'WARNING failed to create child node presenter for node ({child.type})')
                pass
            else:
                self._child_presenters.append(child_presenter)

            idx += 1
            cur_node_type = child.type

    def __str__(self):
        return ''.join([str(child_presenter) for child_presenter in self._child_presenters])

    @property
    def node(self) -> Node:
        return self._node

    @property
    def child_presenters(self) -> list:
        return self._child_presenters


class ParagraphPresenter(NodePresenter):
    _no_leading_newlines: bool

    def __init__(self, node: Node, no_leading_newlines=False):
        super().__init__(node)

        self._no_leading_newlines = no_leading_newlines

    def __str__(self):
        out = ''
        if not self._no_leading_newlines:
            out += '\n'
        out += ''.join([str(child_presenter) for child_presenter in self._child_presenters])

        return out


class DatePresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self) -> str:
        if self.node.date_value is None:  # type:ignore[attr-defined]
            return ''
        return str(self.node.date_value)  # type:ignore[attr-defined]


class TextPresenter(NodePresenter):
    # _text_node: TextNode

    def __init__(self, node: Node):
        super().__init__(node)

        # self._text_node = TextNode(self._node)

    def __str__(self):
        out = self._node.text

        if self.node.is_bold:
            out = bold(out)

        if self.node.is_italic:
            out = italic(out)

        if self.node.link:
            out = link(out, self.node.link)

        return out


class InlineCardPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        return self.node.url or ''


class HardBreakPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        return '  \n'


class BulletListPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        bulleted_list = []
        for child_presenter in self._child_presenters:
            bulleted_list.append(f'- {str(child_presenter)}')

        return '\n'.join(bulleted_list)


class ListItemPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        bulleted_list = []
        for child_presenter in self._child_presenters:
            bulleted_list.append(str(child_presenter))

        return '\n'.join(bulleted_list)


class OrderedListItemPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        ordered_list = []
        index = self.node.order or 1
        for child_presenter in self._child_presenters:
            ordered_list.append(f'{index}. {str(child_presenter)}')
            index += 1

        return '\n'.join(ordered_list)


class PanelPresenter(NodePresenter):
    def __init__(self, node: Node, no_leading_newlines=False):
        super().__init__(node)

    def __str__(self):
        out_lines = []
        for child_presenter in self._child_presenters:
            cur_presenter_lines = str(child_presenter).splitlines()
            for line in cur_presenter_lines:
                out_lines.append(f'> {line}')

        return '\n'.join(out_lines)


class TablePresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        row_list = []
        for row_presenter in self._child_presenters:
            row_list.append(f'{str(row_presenter)}')

            is_header = (
                len(
                    list(
                        filter(
                            lambda child_child: child_child.node.type == NodeType.TABLE_HEADER,
                            row_presenter.child_presenters,
                        )
                    )
                )
                > 0
            )
            if is_header:
                # insert separator like this:
                # | --- | --- | --- |
                col_count = row_presenter.column_count
                row_list.append(f'| {" | ".join(["---"] * col_count)} |')

        return '\n'.join(row_list)


class TableRowPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        return f'| {" | ".join([str(child_presenter) for child_presenter in self._child_presenters])} |'

    @property
    def column_count(self) -> int:
        return self.node.column_count  # type:ignore[attr-defined]


class TableHeaderPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)


class TableCellPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)


class DocPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        bulleted_list = []
        for child_presenter in self._child_presenters:
            bulleted_list.append(str(child_presenter))

        return '\n'.join(bulleted_list)


class MentionPresenter(NodePresenter):
    def __init__(self, node: Node):
        super().__init__(node)

    def __str__(self):
        return self._node.text


class BlockQuotePresenter(NodePresenter):
    def __str__(self):
        quoted_list = []
        for child_presenter in self._child_presenters:
            quoted_list.append(f'> {str(child_presenter)}')

        return '\n'.join(quoted_list)


class CodeBlockPresenter(NodePresenter):
    def __str__(self):
        if self.node.language:
            quoted_list = [f'```{self.node.language}']
        else:
            quoted_list = ['```']
        for child_presenter in self._child_presenters:
            quoted_list.append(str(child_presenter))

        quoted_list.append('```')
        return '\n'.join(quoted_list)


class ExpandPresenter(NodePresenter):
    def __str__(self):
        expand_list = ['<details>', f'<summary>{self.node.expand_title}</summary>\n']
        for child_presenter in self._child_presenters:
            expand_list.append(str(child_presenter))
        expand_list.append('</details>')
        return '\n'.join(expand_list)


class HeadingPresenter(NodePresenter):
    def __str__(self):
        heading_level = '#' * (self.node.level or 1)
        items = [f'{heading_level}']
        for child_presenter in self._child_presenters:
            items.append(str(child_presenter))
        return ' '.join(items)


class MediaSinglePresenter(NodePresenter):
    def __str__(self):
        return 'view-attachments'


class MediaPresenter(NodePresenter):
    def __str__(self):
        return 'view-attachments'


class EmojiPresenter(NodePresenter):
    def __str__(self):
        return self.node.text or self.node.short_name or '[emoji]'


def create_node_presenter_from_node(
    node: Node, is_first: bool, is_prev_hard_break: bool, parent_node: Optional[Node] = None
) -> NodePresenter:
    if node.type == NodeType.PARAGRAPH:
        no_leading_newlines = (
            not parent_node
            or is_first
            or is_prev_hard_break
            or bool(parent_node and parent_node.type == NodeType.LIST_ITEM)
        )
        return ParagraphPresenter(node, no_leading_newlines)
    elif node.type == NodeType.TEXT:
        return TextPresenter(node)
    elif node.type == NodeType.HARD_BREAK:
        return HardBreakPresenter(node)
    elif node.type == NodeType.BULLET_LIST:
        return BulletListPresenter(node)
    elif node.type == NodeType.LIST_ITEM:
        return ListItemPresenter(node)
    elif node.type == NodeType.PANEL:
        return PanelPresenter(node)
    elif node.type == NodeType.TABLE:
        return TablePresenter(node)
    elif node.type == NodeType.TABLE_ROW:
        return TableRowPresenter(node)
    elif node.type == NodeType.TABLE_HEADER:
        return TableHeaderPresenter(node)
    elif node.type == NodeType.TABLE_CELL:
        return TableCellPresenter(node)
    elif node.type == NodeType.DOC:
        return DocPresenter(node)
    elif node.type == NodeType.MENTION:
        return MentionPresenter(node)
    elif node.type == NodeType.ORDERED_LIST:
        return OrderedListItemPresenter(node)
    elif node.type == NodeType.INLINE_CARD:
        return InlineCardPresenter(node)
    elif node.type == NodeType.BLOCKQUOTE:
        return BlockQuotePresenter(node)
    elif node.type == NodeType.CODE_BLOCK:
        return CodeBlockPresenter(node)
    elif node.type == NodeType.EXPAND:
        return ExpandPresenter(node)
    elif node.type == NodeType.HEADING:
        return HeadingPresenter(node)
    elif node.type == NodeType.MEDIA_SINGLE:
        return MediaSinglePresenter(node)
    elif node.type == NodeType.MEDIA:
        return MediaPresenter(node)
    elif node.type == NodeType.EMOJI:
        return EmojiPresenter(node)
    elif node.type == NodeType.DATE:
        return DatePresenter(node)
    raise NotImplementedError(f"markdown presenter: unhandled node type '{node.type}'")


def header1(text: str) -> str:
    return f'# {text}'


def header2(text: str) -> str:
    return f'## {text}'


def header3(text: str) -> str:
    return f'### {text}'


def bold(text: str) -> str:
    return _apply_formatting(text, '**')


def italic(text: str) -> str:
    return _apply_formatting(text, '*')


def link(text: str, url: str) -> str:
    return f'[{text}]({url})'


def _apply_formatting(text: str, format_symbols: str) -> str:
    text, trailing_spaces_count = remove_trailing_spaces(text)
    return f'{format_symbols}{text}{format_symbols}{" " * trailing_spaces_count}'


def remove_trailing_spaces(text: str) -> tuple[str, int]:
    count = 0
    for ch in reversed(text):
        if ch == ' ':
            count += 1
        else:
            break

    # remove trailing spaces and return that string;
    # str[:0] will clear the string, take it into account by using if ... else
    return text[:-count] if count > 0 else text, count
