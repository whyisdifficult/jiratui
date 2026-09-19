from jiratui.utils.adf import convert_markdown_to_adf
from jiratui.utils.mentions import (
    build_mention_token,
    expand_mention_tokens,
    render_mention_markup,
)


def test_build_mention_token():
    assert (
        build_mention_token('Homer Simpson', '557058:abc-123') == '@[Homer Simpson](557058:abc-123)'
    )


def test_build_mention_token_sanitizes_brackets_in_name():
    # square brackets would break the token grammar and are stripped
    assert build_mention_token('Bart [the] Brat', 'id-1') == '@[Bart the Brat](id-1)'


def test_build_mention_token_sanitizes_parentheses_in_account_id():
    assert build_mention_token('Lisa', 'id(9)') == '@[Lisa](id9)'


def test_render_mention_markup():
    assert (
        render_mention_markup('Homer Simpson', '557058:abc-123')
        == '<span adf="mention" params=\'{"id":"557058:abc-123"}\'>@Homer Simpson</span>'
    )


def test_expand_mention_tokens_without_tokens_returns_input_unchanged():
    text = 'Just a regular comment with an email user@example.com and a [link](http://x)'
    assert expand_mention_tokens(text) == text


def test_expand_mention_tokens_empty_string():
    assert expand_mention_tokens('') == ''


def test_expand_mention_tokens_single_token():
    result = expand_mention_tokens('Hey @[Homer Simpson](abc-123) please review')
    assert result == (
        'Hey <span adf="mention" params=\'{"id":"abc-123"}\'>@Homer Simpson</span> please review'
    )


def test_expand_mention_tokens_multiple_tokens():
    result = expand_mention_tokens('@[Homer](a) and @[Bart](b)')
    assert result == (
        '<span adf="mention" params=\'{"id":"a"}\'>@Homer</span> and '
        '<span adf="mention" params=\'{"id":"b"}\'>@Bart</span>'
    )


def test_expand_mention_tokens_inside_markdown_formatting():
    # a token wrapped in bold markdown must still expand
    result = expand_mention_tokens('**@[Homer](a)**')
    assert result == '**<span adf="mention" params=\'{"id":"a"}\'>@Homer</span>**'


def test_expand_mention_tokens_unicode_name():
    result = expand_mention_tokens('@[Homère Simpson](id-é)')
    assert '>@Homère Simpson</span>' in result
    assert '"id":"id-é"' in result


def test_mention_token_round_trips_to_adf_mention_node():
    markdown = expand_mention_tokens('Hey @[Homer Simpson](557058:abc-123)!')
    adf = convert_markdown_to_adf(markdown)
    nodes = [
        node
        for paragraph in adf['content']
        for node in paragraph.get('content', [])
        if node.get('type') == 'mention'
    ]
    assert len(nodes) == 1
    assert nodes[0]['attrs']['id'] == '557058:abc-123'
    assert nodes[0]['attrs']['text'] == '@Homer Simpson'


def test_multiple_mention_tokens_round_trip_to_adf():
    markdown = expand_mention_tokens('@[Homer](a-1) ping @[Bart](b-2)')
    adf = convert_markdown_to_adf(markdown)
    nodes = [
        node
        for paragraph in adf['content']
        for node in paragraph.get('content', [])
        if node.get('type') == 'mention'
    ]
    assert [node['attrs']['id'] for node in nodes] == ['a-1', 'b-2']
