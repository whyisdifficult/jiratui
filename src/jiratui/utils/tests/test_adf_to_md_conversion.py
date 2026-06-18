import pytest

from jiratui.utils.adf import convert_adf_to_markdown, convert_markdown_to_adf


def test_adf_text():
    # GIVEN
    adf_text = {
        'version': 1,
        'type': 'doc',
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_text)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == 'Hello world\n'
    assert adf == adf_text


def test_adf_blockquote():
    # GIVEN
    adf_blockquote = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'blockquote',
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_blockquote)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '> Hello world\n'
    assert adf == adf_blockquote


def test_adf_inline_card():
    adf_inline_card = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [{'type': 'inlineCard', 'attrs': {'url': 'https://atlassian.com'}}],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_inline_card)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert (
        markdown == '<a adf="inlineCard" href="https://atlassian.com">https://atlassian.com</a>\n'
    )
    assert adf == adf_inline_card


def test_adf_mark_hard_break():
    adf_hard_break = {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {'type': 'text', 'text': 'Hello'},
                    {'type': 'hardBreak', 'attrs': {'text': '\n'}},
                    {'type': 'text', 'text': 'world'},
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_hard_break)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == 'Hello<br>world\n'
    assert adf == {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {'type': 'text', 'text': 'Hello'},
                    {'type': 'hardBreak'},
                    {'type': 'text', 'text': 'world'},
                ],
            }
        ],
    }


def test_adf_expand():
    adf_expand = {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'type': 'expand',
                'attrs': {'title': 'Hello world'},
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_expand)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert (
        markdown
        == """<details adf="expand">

<summary>Hello world</summary>

Hello world

</details>
"""
    )
    assert adf == adf_expand


def test_adf_nested_expand():
    adf_nested_expand = {
        'type': 'doc',
        'version': 1,
        'content': [
            {
                'type': 'nestedExpand',
                'attrs': {'title': 'Hello world'},
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_nested_expand)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert (
        markdown
        == """<details adf="nestedExpand">

<summary>Hello world</summary>

Hello world

</details>
"""
    )
    assert adf == {
        'type': 'doc',
        'version': 1,
        'content': [],
    }


def test_adf_panel():
    adf_panel = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'panel',
                'attrs': {'panelType': 'info'},
                'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_panel)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert (
        markdown
        == """<aside adf="panel" params='{"panelType":"info"}'>

Hello world

</aside>
"""
    )
    assert adf == adf_panel


def test_adf_status():
    adf_status = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'status',
                        'attrs': {
                            'text': 'In Progress',
                            'color': 'yellow',
                        },
                    }
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_status)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == """<span adf="status" params='{"color":"yellow"}'>`In Progress`</span>\n"""
    assert adf == adf_status


def test_adf_bulletlist():
    adf_bulletlist = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'bulletList',
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Item 1'}]}
                        ],
                    },
                    {
                        'type': 'listItem',
                        'content': [
                            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Item 2'}]}
                        ],
                    },
                ],
            }
        ],
    }

    # WHEN
    markdown = convert_adf_to_markdown(adf_bulletlist)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '- Item 1\n- Item 2\n'
    assert adf == adf_bulletlist


def test_adf_codeblock():
    adf_codeblock = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'codeBlock',
                'attrs': {'language': 'javascript'},
                'content': [{'type': 'text', 'text': 'var foo = {};\nvar bar = [];'}],
            }
        ],
    }

    # WHEN
    markdown = convert_adf_to_markdown(adf_codeblock)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert (
        markdown
        == """```javascript
var foo = {};
var bar = [];
```
"""
    )
    assert adf == adf_codeblock


def test_adf_date():
    adf_date = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [{'type': 'date', 'attrs': {'timestamp': '1778803200000'}}],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_date)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '<time adf="date" datetime="1778803200000">2026-05-15</time>\n'
    assert adf == adf_date


def test_adf_mark_link():
    adf_link = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': 'link to a page',
                        'marks': [{'type': 'link', 'attrs': {'href': 'https://jiratui.sh'}}],
                    }
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_link)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '[link to a page](<https://jiratui.sh>)\n'
    assert adf == adf_link


def test_adf_emoji():
    adf_emoji = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {'type': 'text', 'text': 'Talk to '},
                    {
                        'type': 'emoji',
                        'attrs': {
                            'shortName': '😀',
                            'id': '1f600',
                            'text': '😀',
                            'localId': '4ef47dd4830f',
                        },
                    },
                ],
                'attrs': {'localId': '78186273d3f9'},
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_emoji)
    # THEN
    assert (
        markdown
        == 'Talk to <span adf="emoji" params=\'{"shortName":"😀","id":"1f600"}\'>😀</span>\n'
    )


@pytest.mark.parametrize(
    'level, expected_md',
    [
        (1, '# Testing the BackendEnd\n'),
        (2, '## Testing the BackendEnd\n'),
        (3, '### Testing the BackendEnd\n'),
        (4, '#### Testing the BackendEnd\n'),
        (5, '##### Testing the BackendEnd\n'),
        (6, '###### Testing the BackendEnd\n'),
    ],
)
def test_adf_heading(level, expected_md):
    adf_heading = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'heading',
                'attrs': {
                    'level': level,
                },
                'content': [{'type': 'text', 'text': 'Testing the BackendEnd'}],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_heading)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == expected_md
    assert adf == adf_heading


def test_adf_paragraph():
    adf_paragraph = {
        'version': 1,
        'type': 'doc',
        'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello world'}]}],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_paragraph)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == 'Hello world\n'
    assert adf == adf_paragraph


def test_adf_rule():
    adf_rule = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'rule',
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_rule)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '---\n'
    assert adf == adf_rule


def test_adf_decision_list():
    adf_decision_list = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'decisionList',
                'content': [
                    {
                        'type': 'decisionItem',
                        'content': [{'type': 'text', 'text': 'Some Question.'}],
                        'attrs': {
                            'localId': '3464c3d4-8b43-43b8-b313-c6232e3f2636',
                            'state': 'DECIDED',
                        },
                    }
                ],
                'attrs': {'localId': 'c8842e9c-6e63-4e6f-bf98-7a6b4f93b4a3'},
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_decision_list)
    # THEN
    assert (
        markdown
        == """<ul adf="decisionList">

<li adf="decisionItem" params='{"state":"DECIDED"}'>Some Question.</li>

</ul>
"""
    )


def test_adf_ordered_list():
    adf_ordered_list = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'orderedList',
                'attrs': {'order': 1, 'localId': 'a5910d801aef'},
                'content': [
                    {
                        'type': 'listItem',
                        'content': [
                            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Value 1'}]}
                        ],
                    },
                    {
                        'type': 'listItem',
                        'content': [
                            {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Value 2'}]}
                        ],
                    },
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_ordered_list)
    # THEN
    assert markdown == '1. Value 1\n2. Value 2\n'


def test_adf_task_list():
    adf_task_list = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'taskList',
                'content': [
                    {
                        'type': 'taskItem',
                        'content': [{'type': 'text', 'text': 'Task 1'}],
                        'attrs': {'localId': '4b3a', 'state': 'TODO'},
                    },
                    {
                        'type': 'taskItem',
                        'content': [{'type': 'text', 'text': 'Task 2.'}],
                        'attrs': {'localId': '046d', 'state': 'DONE'},
                    },
                ],
                'attrs': {'localId': 'd22464b0-7ca6-4a45-aa52-bd95084051c0'},
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_task_list)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '- [ ] Task 1\n- [x] Task 2.\n'
    assert adf['version'] == 1
    assert adf['type'] == 'doc'
    assert adf['content'][0]['type'] == 'taskList'
    assert adf['content'][0]['content'][0]['type'] == 'taskItem'
    assert adf['content'][0]['content'][0]['content'][0]['type'] == 'text'
    assert adf['content'][0]['content'][0]['content'][0]['text'] == 'Task 1'
    assert adf['content'][0]['content'][1]['type'] == 'taskItem'
    assert adf['content'][0]['content'][1]['content'][0]['type'] == 'text'
    assert adf['content'][0]['content'][1]['content'][0]['text'] == 'Task 2.'
    assert len(adf['content'][0]['content']) == 2


def test_adf_table():
    adf_table = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'table',
                'attrs': {
                    'isNumberColumnEnabled': False,
                    'layout': 'default',
                    'localId': 'ead35c03-f6e4-4b56-83d2-95878309d6dd',
                },
                'content': [
                    {
                        'type': 'tableRow',
                        'attrs': {'localId': '9259b5b3f4b2'},
                        'content': [
                            {
                                'type': 'tableHeader',
                                'attrs': {'localId': '8dc1f9fb0c2e'},
                                'content': [
                                    {
                                        'type': 'paragraph',
                                        'content': [{'type': 'text', 'text': 'Element'}],
                                        'attrs': {'localId': 'a5c73b1a9246'},
                                    }
                                ],
                            },
                            {
                                'type': 'tableHeader',
                                'attrs': {'localId': '8e4fbc8cf053'},
                                'content': [
                                    {
                                        'type': 'paragraph',
                                        'content': [{'type': 'text', 'text': 'Usage'}],
                                        'attrs': {'localId': '6c5ba9a0869f'},
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        'type': 'tableRow',
                        'attrs': {'localId': '17b6f6457f48'},
                        'content': [
                            {
                                'type': 'tableCell',
                                'attrs': {'localId': '8ddd75dce999'},
                                'content': [
                                    {
                                        'type': 'paragraph',
                                        'content': [
                                            {
                                                'type': 'text',
                                                'text': 'Headings',
                                                'marks': [{'type': 'strong'}],
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                'type': 'tableCell',
                                'attrs': {'localId': '98eeb290aae0'},
                                'content': [
                                    {
                                        'type': 'paragraph',
                                        'content': [
                                            {
                                                'type': 'text',
                                                'text': 'Main title and section headers',
                                            }
                                        ],
                                        'attrs': {'localId': '7ce1d7f49ca4'},
                                    }
                                ],
                            },
                        ],
                    },
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_table)
    # THEN
    assert (
        markdown
        == """<div adf="table" params='{"layout":"default","isNumberColumnEnabled":false}'></div>

| Element | Usage |
| --- | --- |
| **Headings** | Main title and section headers |
"""
    )


def test_adf_mention():
    adf_mention = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {'type': 'text', 'text': 'Let’s also menton a user here '},
                    {
                        'type': 'mention',
                        'attrs': {'id': '1', 'text': '@G~', 'accessLevel': '', 'localId': '46'},
                    },
                    {'type': 'text', 'text': ' '},
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_mention)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert (
        markdown
        == 'Let’s also menton a user here <span adf="mention" params=\'{"id":"1","accessLevel":""}\'>@G\~</span> \n'
    )
    assert adf['version'] == 1
    assert adf['type'] == 'doc'
    assert adf['content'][0]['type'] == 'paragraph'
    assert adf['content'][0]['content'][0]['type'] == 'text'
    assert adf['content'][0]['content'][0]['text'] == 'Let’s also menton a user here '
    assert adf['content'][0]['content'][1]['type'] == 'mention'
    assert adf['content'][0]['content'][1]['attrs']['text'] == '@G~'
    assert len(adf['content'][0]['content']) == 2


def test_adf_mark_strong():
    adf_mark_strong = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {'type': 'text', 'text': 'Objective', 'marks': [{'type': 'strong'}]},
                    {'type': 'text', 'text': ': Implement user authentication system'},
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_mark_strong)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '**Objective**: Implement user authentication system\n'
    assert adf == adf_mark_strong


def test_adf_mark_strike():
    adf_mark_strike = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [{'type': 'text', 'text': 'Objective', 'marks': [{'type': 'strike'}]}],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_mark_strike)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '~~Objective~~\n'
    assert adf == adf_mark_strike


def test_adf_mark_em():
    adf_mark_em = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [{'type': 'text', 'text': 'Objective', 'marks': [{'type': 'em'}]}],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_mark_em)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '*Objective*\n'
    assert adf == adf_mark_em


def test_adf_mark_underline():
    adf_mark_underline = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {'type': 'text', 'text': 'Objective', 'marks': [{'type': 'underline'}]}
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_mark_underline)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '<u adf="underline">Objective</u>\n'
    assert adf == adf_mark_underline


def test_adf_mark_text_color():
    adf_mark_text_color = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': 'Objective',
                        'marks': [{'type': 'textColor', 'attrs': {'color': '#97a0af'}}],
                    }
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_mark_text_color)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '<span adf="textColor" params=\'{"color":"#97a0af"}\'>Objective</span>\n'
    assert adf == adf_mark_text_color


def test_adf_mark_subsup():
    adf_subsup = {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': 'Hello world',
                        'marks': [{'type': 'subsup', 'attrs': {'type': 'sub'}}],
                    }
                ],
            }
        ],
    }
    # WHEN
    markdown = convert_adf_to_markdown(adf_subsup)
    adf = convert_markdown_to_adf(markdown)
    # THEN
    assert markdown == '<sub adf="subSup">Hello world</sub>\n'
    assert adf == adf_subsup
