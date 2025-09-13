from unittest.mock import Mock, patch

import pytest

from jiratui.utils.adf2md.adf2md import adf2md
from jiratui.utils.adf2md.markdown import (
    BulletListPresenter,
    DocPresenter,
    HardBreakPresenter,
    ListItemPresenter,
    NodePresenter,
    PanelPresenter,
    TableCellPresenter,
    TableHeaderPresenter,
    TablePresenter,
    TableRowPresenter,
    TextPresenter,
    create_node_presenter_from_node,
    gen_md_from_root_node,
)
from jiratui.utils.adf2md.nodes import (
    BlockQuoteNode,
    BulletListNode,
    CodeBlockNode,
    DateNode,
    DocNode,
    EmojiNode,
    ExpandNode,
    HardBreakNode,
    HeadingNode,
    InlineCardNode,
    ListItemNode,
    MediaInlineNode,
    MediaNode,
    MediaSingleNode,
    MentionNode,
    OrderedListNode,
    PanelNode,
    ParagraphNode,
    RuleNode,
    TableCell,
    TableHeader,
    TableNode,
    TableRow,
    TaskItemNode,
    TaskListNode,
    TextNode,
    create_node_from_dict,
    create_nodes_from_list,
)


def test_adf2md():
    result = adf2md([])
    assert result == ''


@patch('jiratui.utils.adf2md.adf2md.create_nodes_from_list')
def test_adf2md_with_list(create_nodes_from_list_mock: Mock):
    # GIVEN
    create_nodes_from_list_mock.return_value = [
        ParagraphNode({'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world!'}]})
    ]
    # WHEN
    result = adf2md([])
    # THEN
    assert result == 'hello world!'


@patch('jiratui.utils.adf2md.adf2md.create_node_from_dict')
def test_adf2md_with_dict(create_node_from_dict_mock: Mock):
    # GIVEN
    create_node_from_dict_mock.return_value = ParagraphNode(
        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world!'}]}
    )
    # WHEN
    result = adf2md({})
    # THEN
    assert result == 'hello world!'


@patch('jiratui.utils.adf2md.adf2md.create_node_from_dict')
def test_adf2md_with_dict_without_creating_node(create_node_from_dict_mock: Mock):
    # GIVEN
    create_node_from_dict_mock.return_value = None
    # WHEN
    result = adf2md({})
    # THEN
    assert result == ''


@patch('jiratui.utils.adf2md.adf2md.create_nodes_from_list')
def test_adf2md_with_multiple_nodes(create_nodes_from_list_mock: Mock):
    # GIVEN
    create_nodes_from_list_mock.return_value = [
        ParagraphNode({'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello world!'}]}),
        ParagraphNode({'type': 'paragraph', 'content': [{'type': 'text', 'text': 'I am'}]}),
    ]
    # WHEN
    result = adf2md([])
    # THEN
    assert result == 'hello world!\n\nI am'


def test_create_node_from_dict_without_type():
    assert create_node_from_dict({}) is None


def test_create_node_from_dict_not_implemented_node_type():
    with pytest.raises(NotImplementedError, match="unhandled node type 'foo'"):
        create_node_from_dict({'type': 'foo'})


@pytest.mark.parametrize(
    'node_value, expected_node_type',
    [
        ({'type': 'text', 'text': 'hello world!'}, TextNode),
        (
            {
                'version': 1,
                'type': 'doc',
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            },
            DocNode,
        ),
        (
            {
                'type': 'mention',
                'attrs': {
                    'id': 'ABCDE-ABCDE-ABCDE-ABCDE',
                    'text': '@Bradley Ayers',
                    'userType': 'APP',
                },
            },
            MentionNode,
        ),
        (
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]},
            ParagraphNode,
        ),
        ({'type': 'hardBreak'}, HardBreakNode),
        (
            {
                'type': 'bulletList',
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': 'Hello world'}],
                            }
                        ],
                    }
                ],
            },
            BulletListNode,
        ),
        (
            {
                'type': 'listItem',
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            },
            ListItemNode,
        ),
        (
            {
                'type': 'panel',
                'attrs': {'panelType': 'info'},
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            },
            PanelNode,
        ),
        (
            {
                'type': 'table',
                'attrs': {
                    'isNumberColumnEnabled': False,
                    'layout': 'center',
                    'width': 900,
                    'displayMode': 'default',
                },
                'content': [
                    {
                        'type': 'tableRow',
                        'content': [
                            {
                                'type': 'tableCell',
                                'attrs': {},
                                'content': [
                                    {
                                        'type': 'paragraph',
                                        'content': [{'type': 'text', 'text': ' Row one, cell one'}],
                                    }
                                ],
                            },
                            {
                                'type': 'tableCell',
                                'attrs': {},
                                'content': [
                                    {
                                        'type': 'paragraph',
                                        'content': [{'type': 'text', 'text': 'Row one, cell two'}],
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
            TableNode,
        ),
        (
            {
                'type': 'tableRow',
                'content': [
                    {
                        'type': 'tableHeader',
                        'attrs': {},
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': 'Heading one',
                                        'marks': [{'type': 'strong'}],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            TableRow,
        ),
        (
            {
                'type': 'tableHeader',
                'attrs': {},
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': 'Hello world header'}],
                    }
                ],
            },
            TableHeader,
        ),
        (
            {
                'type': 'tableCell',
                'attrs': {},
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            },
            TableCell,
        ),
        (
            {
                'type': 'orderedList',
                'attrs': {'order': 3},
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': 'Hello world'}],
                            }
                        ],
                    }
                ],
            },
            OrderedListNode,
        ),
        ({'type': 'inlineCard', 'attrs': {'url': 'https://atlassian.com'}}, InlineCardNode),
        (
            {
                'type': 'blockquote',
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            },
            BlockQuoteNode,
        ),
        (
            {
                'type': 'codeBlock',
                'attrs': {'language': 'javascript'},
                'content': [{'type': 'text', 'text': 'var foo = {};\nvar bar = [];'}],
            },
            CodeBlockNode,
        ),
        (
            {
                'type': 'expand',
                'attrs': {'title': 'Hello world'},
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            },
            ExpandNode,
        ),
        (
            {
                'type': 'heading',
                'attrs': {'level': 1},
                'content': [{'type': 'text', 'text': 'Heading 1'}],
            },
            HeadingNode,
        ),
        (
            {
                'type': 'mediaSingle',
                'attrs': {'layout': 'center'},
                'content': [
                    {
                        'type': 'media',
                        'attrs': {
                            'id': '4478e39c-cf9b-41d1-ba92-68589487cd75',
                            'type': 'file',
                            'collection': 'MediaServicesSample',
                            'alt': 'moon.jpeg',
                            'width': 225,
                            'height': 225,
                        },
                    }
                ],
            },
            MediaSingleNode,
        ),
        (
            {
                'type': 'media',
                'attrs': {
                    'id': '4478e39c-cf9b-41d1-ba92-68589487cd75',
                    'type': 'file',
                    'collection': 'MediaServicesSample',
                    'alt': 'moon.jpeg',
                    'width': 225,
                    'height': 225,
                },
                'marks': [
                    {
                        'type': 'link',
                        'attrs': {
                            'href': 'https://developer.atlassian.com/platform/atlassian-document-format/concepts/document-structure/nodes/media/#media'
                        },
                    },
                    {'type': 'border', 'attrs': {'color': '#091e4224', 'size': 2}},
                    {
                        'type': 'annotation',
                        'attrs': {
                            'id': 'c4cbe18e-9902-4734-bf9b-1426a81ef785',
                            'annotationType': 'inlineComment',
                        },
                    },
                ],
            },
            MediaNode,
        ),
        ({'type': 'emoji', 'attrs': {'shortName': ':grinning:', 'text': '😀'}}, EmojiNode),
        ({'type': 'date', 'attrs': {'timestamp': '1582152559'}}, DateNode),
        ({'type': 'rule'}, RuleNode),
        (
            {'type': 'mediaInline', 'attrs': {'id': '1', 'collection': 'c', 'height': 12}},
            MediaInlineNode,
        ),
        (
            {
                'type': 'taskList',
                'content': [
                    {
                        'type': 'taskItem',
                        'content': [{'type': 'text', 'text': 'Text 1'}],
                        'attrs': {'localId': '75', 'state': 'DONE'},
                    },
                    {
                        'type': 'taskItem',
                        'content': [{'type': 'text', 'text': 'Another text“'}],
                        'attrs': {'localId': '228', 'state': 'DONE'},
                    },
                    {
                        'type': 'taskItem',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'some text',
                                'marks': [{'type': 'link', 'attrs': {'href': 'http://foo.bar'}}],
                            }
                        ],
                        'attrs': {'localId': '522', 'state': 'DONE'},
                    },
                ],
                'attrs': {'localId': 'bebd81b'},
            },
            TaskListNode,
        ),
        (
            {
                'type': 'taskItem',
                'content': [{'type': 'text', 'text': 'Another text“'}],
                'attrs': {'localId': '228', 'state': 'DONE'},
            },
            TaskItemNode,
        ),
    ],
)
def test_create_node_from_dict(node_value, expected_node_type):
    result = create_node_from_dict(node_value)
    assert isinstance(result, expected_node_type)


def test_create_nodes_from_list():
    result = create_nodes_from_list(
        [
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]},
            {
                'type': 'heading',
                'attrs': {'level': 1},
                'content': [{'type': 'text', 'text': 'Heading 1'}],
            },
        ]
    )
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], ParagraphNode)
    assert isinstance(result[1], HeadingNode)


def test_gen_md_from_root_node():
    # WHEN
    result = gen_md_from_root_node(DateNode({'type': 'date', 'attrs': {'timestamp': '1582152559'}}))
    # THEN
    assert isinstance(result, str)
    assert result == '2020-02-19'


@patch('jiratui.utils.adf2md.markdown.create_node_presenter_from_node')
def test_gen_md_from_root_node_with_error(create_node_presenter_from_node_mock: Mock):
    # GIVEN
    create_node_presenter_from_node_mock.side_effect = ValueError
    # WHEN
    result = gen_md_from_root_node(DateNode({'type': 'date', 'attrs': {'timestamp': '1582152559'}}))
    # THEN
    assert result == ''


def test_create_node_presenter_without_children():
    # WHEN
    np = NodePresenter(DateNode({'type': 'date', 'attrs': {'timestamp': '1582152559'}}))
    # THEN
    assert str(np) == ''
    assert isinstance(np.node, DateNode)
    assert np.child_presenters == []


@pytest.mark.parametrize(
    'input_node, expected_result',
    [
        (DateNode({'type': 'date', 'attrs': {'timestamp': '1582152559'}}), '2020-02-19'),
        (
            ParagraphNode({'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello'}]}),
            'hello',
        ),
        (TextNode({'type': 'text', 'text': 'hello'}), 'hello'),
        (
            HardBreakNode(
                {
                    'type': 'doc',
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'hello'}, {'type': 'hardBreak'}],
                        }
                    ],
                }
            ),
            'hello  \n',
        ),
        (
            BulletListNode(
                {
                    'type': 'bulletList',
                    'content': [
                        {
                            'type': 'listItem',
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [{'type': 'text', 'text': 'hello'}],
                                }
                            ],
                        }
                    ],
                }
            ),
            '- hello',
        ),
        (
            ListItemNode(
                {
                    'type': 'listItem',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello'}]}
                    ],
                }
            ),
            'hello',
        ),
        (
            PanelNode(
                {
                    'type': 'panel',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'hello'}]}
                    ],
                    'attrs': {'panelType': 'info'},
                }
            ),
            '> hello',
        ),
        (
            TableNode(
                {
                    'type': 'table',
                    'content': [
                        {
                            'type': 'tableRow',
                            'content': [
                                {
                                    'type': 'tableCell',
                                    'attrs': {},
                                    'content': [
                                        {
                                            'type': 'paragraph',
                                            'content': [{'type': 'text', 'text': 'hello'}],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                    'attrs': {
                        'isNumberColumnEnabled': False,
                        'layout': 'center',
                        'width': 900,
                        'displayMode': 'default',
                    },
                }
            ),
            '| hello |',
        ),
        (
            TableRow(
                {
                    'type': 'tableRow',
                    'content': [
                        {
                            'type': 'tableCell',
                            'attrs': {},
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [{'type': 'text', 'text': 'hello'}],
                                }
                            ],
                        }
                    ],
                }
            ),
            '| hello |',
        ),
        (
            TableHeader(
                {
                    'type': 'tableHeader',
                    'attrs': {},
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'Hello world header'}],
                        }
                    ],
                }
            ),
            'Hello world header',
        ),
        (
            TableCell(
                {
                    'type': 'tableCell',
                    'attrs': {},
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            'Hello world',
        ),
        (
            DocNode(
                {
                    'version': 1,
                    'type': 'doc',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            'Hello world',
        ),
        (
            MentionNode(
                {
                    'type': 'mention',
                    'attrs': {
                        'id': 'ABCDE-ABCDE-ABCDE-ABCDE',
                        'text': '@Bart Simpson',
                        'userType': 'APP',
                    },
                }
            ),
            '@Bart Simpson',
        ),
        (
            OrderedListNode(
                {
                    'type': 'orderedList',
                    'attrs': {'order': 3},
                    'content': [
                        {
                            'type': 'listItem',
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [{'type': 'text', 'text': 'Hello world'}],
                                }
                            ],
                        }
                    ],
                }
            ),
            '3. Hello world',
        ),
        (
            InlineCardNode({'type': 'inlineCard', 'attrs': {'url': 'https://foo.bar'}}),
            'https://foo.bar',
        ),
        (
            BlockQuoteNode(
                {
                    'type': 'blockquote',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            '> Hello world',
        ),
        (
            CodeBlockNode(
                {
                    'type': 'codeBlock',
                    'attrs': {'language': 'javascript'},
                    'content': [{'type': 'text', 'text': 'var foo = {};\nvar bar = [];'}],
                }
            ),
            '```javascript\nvar foo = {};\nvar bar = [];\n```',
        ),
        (
            CodeBlockNode(
                {
                    'type': 'codeBlock',
                    'attrs': {'language': 'json'},
                    'content': [{'type': 'text', 'text': '{"a": 1}'}],
                }
            ),
            '```json\n{\n   "a": 1\n}\n```',
        ),
        (
            CodeBlockNode(
                {
                    'type': 'codeBlock',
                    'attrs': {'language': ''},
                    'content': [{'type': 'text', 'text': '{"a": 1}'}],
                }
            ),
            '```\n{"a": 1}\n```',
        ),
        (
            ExpandNode(
                {
                    'type': 'expand',
                    'attrs': {'title': 'Hello Bart'},
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            '<details>\n<summary>Hello Bart</summary>\n\nHello world\n</details>',
        ),
        (
            HeadingNode(
                {
                    'type': 'heading',
                    'attrs': {'level': 1},
                    'content': [{'type': 'text', 'text': 'Heading 1'}],
                }
            ),
            '# Heading 1',
        ),
        (
            MediaSingleNode(
                {
                    'type': 'mediaSingle',
                    'attrs': {'layout': 'center'},
                    'content': [
                        {
                            'type': 'media',
                            'attrs': {
                                'id': '4478e39c-cf9b-41d1-ba92-68589487cd75',
                                'type': 'file',
                                'collection': 'MediaServicesSample',
                                'alt': 'moon.jpeg',
                                'width': 225,
                                'height': 225,
                            },
                        }
                    ],
                }
            ),
            '[see-attachments]',
        ),
        (EmojiNode({'type': 'emoji', 'attrs': {'shortName': ':grinning:', 'text': '😀'}}), '😀'),
        (
            RuleNode(
                {
                    'version': 1,
                    'type': 'doc',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]},
                        {'type': 'rule'},
                    ],
                }
            ),
            'Hello world\n\n---\n',
        ),
        (
            MediaInlineNode(
                {
                    'type': 'mediaInline',
                    'attrs': {'layout': 'center'},
                    'content': [
                        {
                            'type': 'media',
                            'attrs': {
                                'id': '4478e39c-cf9b-41d1-ba92-68589487cd75',
                                'type': 'file',
                                'collection': 'MediaServicesSample',
                                'alt': 'moon.jpeg',
                                'width': 225,
                                'height': 225,
                            },
                        }
                    ],
                }
            ),
            '[see-attachments]',
        ),
        (
            TaskListNode(
                {
                    'type': 'taskList',
                    'content': [
                        {
                            'type': 'taskItem',
                            'content': [{'type': 'text', 'text': 'Text 1'}],
                            'attrs': {'localId': '75', 'state': 'DONE'},
                        },
                        {
                            'type': 'taskItem',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': 'some text',
                                    'marks': [
                                        {'type': 'link', 'attrs': {'href': 'http://foo.bar'}}
                                    ],
                                }
                            ],
                            'attrs': {'localId': '522', 'state': 'DONE'},
                        },
                    ],
                    'attrs': {'localId': 'bebd81b'},
                }
            ),
            '- [x] Text 1\n- [x] [some text](http://foo.bar)',
        ),
        (
            TaskItemNode(
                {
                    'type': 'taskItem',
                    'content': [{'type': 'text', 'text': 'Text 1'}],
                    'attrs': {'localId': '75', 'state': 'To Do'},
                }
            ),
            '[ ] Text 1',
        ),
    ],
)
def test_gen_md_from_root_node_with_use_cases(input_node, expected_result):
    # WHEN
    result = gen_md_from_root_node(input_node)
    # THEN
    assert isinstance(result, str)
    assert result == expected_result


@pytest.mark.parametrize(
    'node, expected_presenter',
    [
        (TextNode({'type': 'text', 'text': 'Hello world'}), TextPresenter),
        (HardBreakNode({'type': 'hardBreak'}), HardBreakPresenter),
        (
            BulletListNode(
                {
                    'type': 'bulletList',
                    'content': [
                        {
                            'type': 'listItem',
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [{'type': 'text', 'text': 'Hello world'}],
                                }
                            ],
                        }
                    ],
                }
            ),
            BulletListPresenter,
        ),
        (
            ListItemNode(
                {
                    'type': 'listItem',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            ListItemPresenter,
        ),
        (
            PanelNode(
                {
                    'type': 'panel',
                    'attrs': {'panelType': 'info'},
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            PanelPresenter,
        ),
        (
            TableNode(
                {
                    'type': 'table',
                    'attrs': {
                        'isNumberColumnEnabled': False,
                        'layout': 'center',
                        'width': 900,
                        'displayMode': 'default',
                    },
                    'content': [
                        {
                            'type': 'tableRow',
                            'content': [
                                {
                                    'type': 'tableCell',
                                    'attrs': {},
                                    'content': [
                                        {
                                            'type': 'paragraph',
                                            'content': [
                                                {'type': 'text', 'text': ' Row one, cell one'}
                                            ],
                                        }
                                    ],
                                },
                                {
                                    'type': 'tableCell',
                                    'attrs': {},
                                    'content': [
                                        {
                                            'type': 'paragraph',
                                            'content': [
                                                {'type': 'text', 'text': 'Row one, cell two'}
                                            ],
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ),
            TablePresenter,
        ),
        (
            TableRow(
                {
                    'type': 'tableRow',
                    'content': [
                        {
                            'type': 'tableHeader',
                            'attrs': {},
                            'content': [
                                {
                                    'type': 'paragraph',
                                    'content': [
                                        {
                                            'type': 'text',
                                            'text': 'Heading one',
                                            'marks': [{'type': 'strong'}],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ),
            TableRowPresenter,
        ),
        (
            TableHeader(
                {
                    'type': 'tableHeader',
                    'attrs': {},
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': 'Hello world header'}],
                        }
                    ],
                }
            ),
            TableHeaderPresenter,
        ),
        (
            TableCell(
                {
                    'type': 'tableCell',
                    'attrs': {},
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            TableCellPresenter,
        ),
        (
            DocNode(
                {
                    'version': 1,
                    'type': 'doc',
                    'content': [
                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                    ],
                }
            ),
            DocPresenter,
        ),
    ],
)
def test_create_node_presenter_from_node(node, expected_presenter):
    # WHEN
    result = create_node_presenter_from_node(node, True, False)
    # THEN
    assert isinstance(result, expected_presenter)
