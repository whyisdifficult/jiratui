from datetime import date, datetime
import enum
from typing import Optional


class NodeType(enum.Enum):
    """The type of ADF nodes supported."""

    PARAGRAPH = (0, 'paragraph')
    TEXT = (1, 'text')
    HARD_BREAK = (2, 'hardBreak')
    BULLET_LIST = (3, 'bulletList')
    LIST_ITEM = (4, 'listItem')
    PANEL = (5, 'panel')
    TABLE = (6, 'table')
    TABLE_ROW = (7, 'tableRow')
    TABLE_HEADER = (8, 'tableHeader')
    TABLE_CELL = (9, 'tableCell')
    DOC = (10, 'doc')
    MENTION = (11, 'mention')
    ORDERED_LIST = (12, 'orderedList')
    INLINE_CARD = (13, 'inlineCard')
    BLOCKQUOTE = (14, 'blockquote')
    CODE_BLOCK = (15, 'codeBlock')
    EXPAND = (16, 'expand')
    HEADING = (17, 'heading')
    MEDIA_SINGLE = (18, 'mediaSingle')
    MEDIA = (19, 'media')
    EMOJI = (20, 'emoji')
    DATE = (21, 'date')

    def __str__(self):
        return self.value[1]

    @classmethod
    def from_string(cls, s):
        for value in cls:
            if value.value[1] == s:
                return value
        raise ValueError(f"enum '{cls.__name__}' doesn't have value with string '{s}'")

    @classmethod
    def supported_values(cls):
        return [e.value[1] for e in NodeType]


class Node(object):
    """The base implementation of a ADF Node."""

    _type: NodeType
    _type_str: str
    _attrs: dict
    _content: list
    _child_nodes: list

    def __init__(self, node_dict: dict):
        if 'type' not in node_dict:
            raise ValueError("node must contain 'type' attribute")

        self._type_str = node_dict['type']
        self._type = NodeType.from_string(self._type_str)
        self._attrs = node_dict['attrs'] if 'attrs' in node_dict else {}
        self._content = node_dict['content'] if 'content' in node_dict else []

        self._child_nodes = []
        for child_node in self._content:
            self._child_nodes.append(create_node_from_dict(child_node))

    @property
    def type(self) -> NodeType:
        return self._type

    @property
    def child_nodes(self) -> list:
        return self._child_nodes


class DateNode(Node):
    """Represents a date ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/date/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)
        if 'timestamp' not in node_dict['attrs']:
            raise ValueError("date node must contain 'attrs.timestamp' attribute")

        self._text = node_dict['attrs']['timestamp']

    @property
    def text(self) -> str:
        return self._text

    @property
    def date_value(self) -> date | None:
        if self._text:
            try:
                return datetime.fromtimestamp(int(self._text)).date()
            except Exception:
                return None
        return None


class ParagraphNode(Node):
    """Represents a paragraph ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/paragraph/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)


class DocNode(Node):
    """Represents a doc ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/doc/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'content' not in node_dict:
            raise ValueError("doc node must contain 'content' attribute")

        self._elements = []
        for child_node in self._child_nodes:
            self._elements.append(child_node)


class MentionNode(Node):
    """Represents a mention ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/mention/
    """

    _text: str

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'attrs' not in node_dict:
            raise ValueError("mention node must contain 'attrs' attribute")

        if 'text' not in node_dict['attrs']:
            raise ValueError("mention node must contain 'attrs.text' attribute")

        self._text = node_dict['attrs']['text']

    @property
    def text(self) -> str:
        return self._text


class TextNode(Node):
    """Represents a text ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/text/
    """

    _text: str
    _marks: list[dict]
    _link: Optional[str] = None
    _is_bold: bool = False
    _is_italic: bool = False

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'text' not in node_dict:
            raise ValueError("text node must contain 'text' attribute")

        self._text = node_dict['text']
        self._marks = node_dict['marks'] if 'marks' in node_dict else []

        for mark in self._marks:
            if 'type' not in mark:
                # print("WARNING mark does not contain 'type' attribute")
                continue

            mark_type = mark['type']

            if mark_type == 'strong':
                self._is_bold = True

            if mark_type == 'em':
                self._is_italic = True

            if mark_type == 'link':
                if 'attrs' not in mark:
                    # print("ERROR link node does not contain 'attrs' attribute")
                    continue

                if 'href' not in mark['attrs']:
                    # print("ERROR link's attrs node does not contain 'href' attribute")
                    continue

                self._link = mark['attrs']['href']

    @property
    def text(self) -> str:
        return self._text

    @property
    def link(self) -> Optional[str]:
        return self._link

    @property
    def is_bold(self) -> bool:
        return self._is_bold

    @property
    def is_italic(self) -> bool:
        return self._is_italic


class BulletListNode(Node):
    """Represents a bulletList ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/bulletList/
    """

    _elements: list[Node]

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        self._elements = []
        for child_node in self._child_nodes:
            # make sure we have only listItem as children of the node
            if child_node.type != NodeType.LIST_ITEM:
                # print(
                #     f"WARNING '{NodeType.LIST_ITEM.value}' expected under bulletList; but '{child_node.type}' appeared"
                # )
                continue
            self._elements.append(child_node)

    @property
    def elements(self) -> list[Node]:
        return self._elements


class ListItemNode(Node):
    """Represents a listItem ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/listItem/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)


class OrderedListNode(Node):
    """The equivalent to the `BulletListNode` but with ordered rendering."""

    _elements: list[Node]
    _order: int

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        self._order = self._attrs.get('order', 1)
        self._elements = []
        for child_node in self._child_nodes:
            # make sure we have only listItem as children of the node
            if child_node.type != NodeType.LIST_ITEM:
                # print(
                #     f"WARNING '{NodeType.LIST_ITEM.value}' expected under orderedList; but '{child_node.type}' appeared"
                # )
                continue
            self._elements.append(child_node)

    @property
    def elements(self) -> list[Node]:
        return self._elements

    @property
    def order(self) -> int:
        return self._order


class BlockQuoteNode(Node):
    """Represents a blockquote ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/blockquote/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)


class CodeBlockNode(Node):
    """Represents a codeBlock ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/codeBlock/
    """

    _language: str

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        self._language = self._attrs.get('language', '')
        self._elements = []
        for child_node in self._child_nodes:
            # make sure we have only text as children of the node
            if child_node.type != NodeType.TEXT:
                # print(
                #     f"WARNING '{NodeType.TEXT.value}' expected under orderedList; but '{child_node.type}' appeared"
                # )
                continue
            self._elements.append(child_node)

    @property
    def language(self) -> str:
        return self._language


class ExpandNode(Node):
    """Represents a expand ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/expand/
    """

    @property
    def expand_title(self) -> str:
        return self._attrs.get('title') or 'Click to expand'


class HeadingNode(Node):
    """Represents a heading ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/heading/
    """

    _level: int

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'attrs' not in node_dict:
            raise ValueError("heading node must contain 'attrs' attribute")

        if 'level' not in node_dict['attrs']:
            raise ValueError("heading node must contain 'attrs.level' attribute")

        self._level = node_dict['attrs']['level']

    @property
    def level(self) -> int:
        return self._level


class MediaSingleNode(Node):
    """Represents a mediaSingle ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/mediaSingle/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'attrs' not in node_dict:
            raise ValueError("mediaSingle node must contain 'attrs' attribute")

        if len(self._child_nodes) == 0:
            raise ValueError('mediaSingle node must contain exactly 1 media node')

        if self._child_nodes[0].type != NodeType.MEDIA:
            raise ValueError(
                "WARNING '{NodeType.MEDIA.value}' expected under mediaSingle; but '{self._child_nodes[0].type}' appeared"
            )

        self._elements = [self._child_nodes[0]]


class MediaNode(Node):
    """Represents a media ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/media/
    """

    _media_id: str
    _media_type: str

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'attrs' not in node_dict:
            raise ValueError("media node must contain 'attrs' attribute")

        if 'type' not in node_dict.get('attrs', {}):
            raise ValueError("media node must contain 'type' attribute")

        if 'id' not in node_dict.get('attrs', {}):
            raise ValueError("media node must contain 'type' attribute")

        self._media_id = node_dict.get('attrs', {}).get('id')
        self._media_type = node_dict.get('attrs', {}).get('type')

    @property
    def media_id(self) -> str:
        return self._media_id

    @property
    def media_type(self) -> str:
        return self._media_type


class EmojiNode(Node):
    """Represents a emoji ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/emoji/
    """

    _short_name: str | None

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'text' not in self._attrs:
            raise ValueError("emoji node must contain 'text' attribute")

        self._text = self._attrs['text']
        self._short_name = self._attrs.get('shortName')

    @property
    def text(self) -> str:
        return self._text

    @property
    def _hort_name(self) -> str:
        return self._short_name


class HardBreakNode(Node):
    """Represents a hardBreak ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/hardBreak/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)


class PanelNode(Node):
    """Represents a panel ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/panel/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)


class TableRow(Node):
    """Represents a tableRow ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_row/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

    @property
    def column_count(self) -> int:
        count = 0
        for child in self.child_nodes:
            if child.type in [NodeType.TABLE_HEADER, NodeType.TABLE_CELL]:
                # TODO add support colspan
                count += child.colspan

        return count


class TableNode(Node):
    """Represents a table ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

    @property
    def header(self) -> Optional[TableRow]:
        headers = list(
            filter(
                lambda node: node.type == NodeType.TABLE_ROW
                and len(
                    list(
                        filter(lambda child: child.type == NodeType.TABLE_HEADER, node.child_nodes)
                    )
                )
                > 0,
                self.child_nodes,
            )
        )

        if len(headers) == 0:
            return None

        # if len(headers) > 0:
        #     print('WARNING table contains more than one header')

        return headers[0]


class TableCell(Node):
    """Represents a tableCell ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_cell/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

    @property
    def colspan(self) -> int:
        return self._attrs['colspan'] if 'colspan' in self._attrs else 1


class TableHeader(TableCell):
    """Represents a tableHeader ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_header/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)


class InlineCardNode(Node):
    """Represents a inlineCardNode ADF node

    See Also:
        https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/inlineCard/
    """

    def __init__(self, node_dict: dict):
        super().__init__(node_dict)

        if 'attrs' not in node_dict:
            raise ValueError("inlineCard node must contain 'attrs' attribute")
        self._url = node_dict['attrs']['url']

    @property
    def url(self) -> Optional[str]:
        return self._url


def create_node_from_dict(node_dict: dict) -> Optional[Node]:
    """Creates a `jiratui.utils.adf2md.nodes.Node` instance that represents an Atlassian's ADF Node.

    Args:
        node_dict: the details of the ADF Node

    Returns:
        An instance of `jiratui.utils.adf2md.nodes.Node` or, `None` if the `type` attribute is missing.

    Raises:
        NotImplementedError: if the type of ADF node is not supported.
    """
    if 'type' not in node_dict:
        return None

    try:
        node_type = NodeType.from_string(node_dict['type'])
    except ValueError as e:
        raise NotImplementedError(f"unhandled node type '{node_dict['type']}'") from e

    if node_type == NodeType.TEXT:
        return TextNode(node_dict)
    if node_type == NodeType.DOC:
        return DocNode(node_dict)
    if node_type == NodeType.MENTION:
        return MentionNode(node_dict)
    if node_type == NodeType.PARAGRAPH:
        return ParagraphNode(node_dict)
    if node_type == NodeType.HARD_BREAK:
        return HardBreakNode(node_dict)
    if node_type == NodeType.BULLET_LIST:
        return BulletListNode(node_dict)
    if node_type == NodeType.LIST_ITEM:
        return ListItemNode(node_dict)
    if node_type == NodeType.PANEL:
        return PanelNode(node_dict)
    if node_type == NodeType.TABLE:
        return TableNode(node_dict)
    if node_type == NodeType.TABLE_ROW:
        return TableRow(node_dict)
    if node_type == NodeType.TABLE_HEADER:
        return TableHeader(node_dict)
    if node_type == NodeType.TABLE_CELL:
        return TableCell(node_dict)
    if node_type == NodeType.ORDERED_LIST:
        return OrderedListNode(node_dict)
    if node_type == NodeType.INLINE_CARD:
        return InlineCardNode(node_dict)
    if node_type == NodeType.BLOCKQUOTE:
        return BlockQuoteNode(node_dict)
    if node_type == NodeType.CODE_BLOCK:
        return CodeBlockNode(node_dict)
    if node_type == NodeType.EXPAND:
        return ExpandNode(node_dict)
    if node_type == NodeType.HEADING:
        return HeadingNode(node_dict)
    if node_type == NodeType.MEDIA_SINGLE:
        return MediaSingleNode(node_dict)
    if node_type == NodeType.MEDIA:
        return MediaNode(node_dict)
    if node_type == NodeType.EMOJI:
        return EmojiNode(node_dict)
    if node_type == NodeType.DATE:
        return DateNode(node_dict)

    raise RuntimeError(f"unhandled node type '{node_type}'")


def create_nodes_from_list(node_dict_list: list[dict]) -> list[Node]:
    """Creates a list of `jiratui.utils.adf2md.nodes.Node` instances that represents a list of Atlassian's ADF Node.

    Args:
        node_dict_list: a list with the details of the ADF nodes.

    Returns:
        A list of instances of `jiratui.utils.adf2md.nodes.Node`.

    Raises:
        NotImplementedError: if the type of ADF node is not supported.
    """
    out: list[Node] = []

    idx = 0
    for node_dict in node_dict_list:
        if not (new_node := create_node_from_dict(node_dict)):
            # print(f'WARNING failed to create node from dict (list_index={idx})')
            pass
        else:
            out.append(new_node)

        idx += 1

    return out
